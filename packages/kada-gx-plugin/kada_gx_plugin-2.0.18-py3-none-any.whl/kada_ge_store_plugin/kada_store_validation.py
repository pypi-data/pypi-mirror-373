"""
Great Expectations plugin to send validation results to
Azure blob storage with custom filename and filepath.

This subpackage needs to be used in Great Expectations
checkpoints actions.
"""

import os
import json
import logging
import importlib.resources
import shutil
from pathlib import Path
from jinja2 import PackageLoader
from typing import Literal, Optional, Union
from typing_extensions import override
from great_expectations.checkpoint import (
    ActionContext,
    CheckpointResult,
    ValidationAction,
)
from great_expectations.compatibility.pydantic import PrivateAttr
from great_expectations.datasource.fluent.config_str import ConfigStr


logger = logging.getLogger(__name__)


class KadaStoreValidationResultsActionException(Exception):
    pass


class KadaStoreValidationResultsAction(ValidationAction):
    """
    Kada Store validation action. It inherits from
    great expection validation action class and implements the
    `_run` method.
    https://github.com/great-expectations/great_expectations/blob/1.1.3/great_expectations/checkpoint/actions.py#L106

    Attributes:
        prefix: The folder path in your container where the .json blob will be stored.
        azure_blob_sas_url: The SAS url for the Azure Storage Account container
        test_directory: Local directory to store the validation results

    Note this is tested to be used by GX Core 1.1.x
    """

    type: Literal["kada"] = "kada"  # Pydantic model
    prefix: Optional[Union[ConfigStr, str]]
    azure_blob_sas_url: Optional[Union[ConfigStr, str]]
    test_directory: Optional[str]
    _storage_client: str = PrivateAttr(default='internal_value')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.test_directory and not self.azure_blob_sas_url:
            raise KadaStoreValidationResultsActionException('Either test_directory or azure_blob_sas_url must be set')

    def _initialize_storage_client(self):
        if self.azure_blob_sas_url:
            from azure.storage.blob import ContainerClient  # Conditional importing
            self._storage_client = ContainerClient.from_container_url(self.azure_blob_sas_url)

    @staticmethod
    def _substitute_storage_credential(storage_credential: ConfigStr | str | None) -> str | None:
        from great_expectations.data_context.data_context.context_factory import project_manager

        config_provider = project_manager.get_config_provider()
        if isinstance(storage_credential, ConfigStr):
            return storage_credential.get_config_value(config_provider=config_provider)
        return storage_credential

    @staticmethod
    def _sanitize_validation_results(run_result_dict: dict) -> dict:
        sensitive_fields = [
            'partial_unexpected_list',
            'partial_unexpected_counts',
            'partial_unexpected_index_list',
            'unexpected_list',
            'unexpected_index_list',
            'unexpected_index_query'
        ]
        for result in run_result_dict.get('results', []):
            result_data = result.get('result', {})
            if not result_data:
                continue
            for field in sensitive_fields:
                result_data.pop(field, None)

    @override
    def run(
        self, checkpoint_result: CheckpointResult, action_context: ActionContext | None = None
    ):
        self.prefix = self._substitute_storage_credential(self.prefix)
        self.azure_blob_sas_url = self._substitute_storage_credential(self.azure_blob_sas_url)
        self._initialize_storage_client()
        run_name = checkpoint_result.run_id.run_name
        run_time = checkpoint_result.run_id.run_time.strftime('%Y%m%dT%H%M%S')
        # Extract kada_targets and place it into the batch_spec this is to conform to the pre GX Core setup
        kada_targets_lookup = {}
        for validation_defs in checkpoint_result.checkpoint_config.validation_definitions:
            data_asset = validation_defs.data.data_asset
            if 'kada_targets' not in data_asset.batch_metadata:
                raise KadaStoreValidationResultsActionException(f'kada_targets not found in batch_metadata for data asset {data_asset.name}, please check that a kada_target has been assigned')
            kada_targets_lookup[validation_defs.id] = data_asset.batch_metadata['kada_targets']
        for validation_result in checkpoint_result.run_results.values():  # This is a dict of ValidationResults objects
            run_result_dict = validation_result.to_json_dict()
            self._sanitize_validation_results(run_result_dict)
            validation_id = run_result_dict['meta']['validation_id']
            kada_targets = kada_targets_lookup[validation_id]
            run_result_dict['meta'].setdefault('batch_spec', {}).setdefault('kada_targets', kada_targets)  # Merge it to batch_spec to align with legacy
            kada_result_file_name = f'{run_name}_{validation_id}_expectation_result_{run_time}.json'
            # We also need to covert type to expectation_type to conform to the old format
            for results in run_result_dict.get('results', []):
                results['expectation_config']['expectation_type'] = results['expectation_config']['type']
            json_object = json.dumps(run_result_dict, indent=2)  # Format the results
            if self.test_directory:
                os.makedirs(f'{self.test_directory}/{self.prefix}', exist_ok=True)
                file_key = os.path.join(f'{self.test_directory}/{self.prefix}', kada_result_file_name)
                with open(file_key, "w") as outfile:
                    outfile.write(json_object)
            else:
                az_blob_key = os.path.join(self.prefix, kada_result_file_name)
                self._storage_client.upload_blob(
                    name=az_blob_key,
                    data=json_object,
                    encoding='utf-8',
                    overwrite=True,
                )


# Monkey Patch Jinja Templates with our Kada version on load by intercepting PackageLoader.get_source
original_get_source = PackageLoader.get_source
def kada_get_source(self, environment, template):
    templates_map = {}  # Map it
    templates_path = Path(importlib.resources.files('kada_ge_store_plugin') / 'data_docs_templates')  # Needs to be relative to the package
    for f in os.listdir(templates_path):
        file_path = os.path.join(templates_path, f)
        if os.path.isfile(file_path):
            with open(file_path, "r") as file:
                templates_map[f] = file.read()

    if template in templates_map:
        return templates_map[template], None, lambda: False  # Return content, None for filename, False for up-to-date check
    # For all other templates, call the original method
    return original_get_source(self, environment, template)

# Patch the method
PackageLoader.get_source = kada_get_source

# Also hide the versions for GX
# https://github.com/great-expectations/great_expectations/blob/c68c279f1013c5a583dc895bcc6763ced6a474b6/great_expectations/render/renderer/page_renderer.py#L449
from great_expectations.render.renderer.page_renderer import ValidationResultsPageRenderer, ExpectationSuitePageRenderer

# Preserve the original method
original_render_validation_info = ValidationResultsPageRenderer._render_validation_info

def remove_versions_render_validation_info(cls, validation_results):
    table_content = original_render_validation_info(validation_results)
    table_content.table.pop(0)  # Remove the versions row
    return table_content


# Preserve the original method
original_render_expectation_suite_info = ExpectationSuitePageRenderer._render_expectation_suite_info

def remove_versions_render_expectation_suite_info(cls, expectations):
    table_content = original_render_expectation_suite_info(expectations)
    table_content.table.pop(1)  # Remove the versions row
    return table_content


# Patch the method
ValidationResultsPageRenderer._render_validation_info = remove_versions_render_validation_info
ExpectationSuitePageRenderer._render_expectation_suite_info = remove_versions_render_expectation_suite_info


# Monkey Patch PandasBatchSpec readers to obfuscate the connection since it has passwords
from great_expectations.core.batch_spec import PandasBatchSpec
from great_expectations.alias_types import JSONValues
og_to_json_dict = PandasBatchSpec.to_json_dict
def new_to_json_dict(self) -> dict[str, JSONValues]:
    jsd = og_to_json_dict(self)
    if jsd["reader_options"].get("con"):
        jsd["reader_options"]["con"] = "******"
    return jsd


PandasBatchSpec.to_json_dict = new_to_json_dict


# Add the KADA Logo to the static assets
static_source_images_path = Path(importlib.resources.files('kada_ge_store_plugin') / 'static/images')  # Needs to be relative to the package
source_file = os.path.join(static_source_images_path, 'KADA_logo.svg')
static_dest_images_path = Path(importlib.resources.files('great_expectations') / 'render/view/static/images')
dest_file = os.path.join(static_dest_images_path, "KADA_logo.svg")
shutil.copy(source_file, dest_file)


# Copy css files to the static image
static_source_css = Path(importlib.resources.files("kada_ge_store_plugin") / "static/css")
for css_file in os.listdir(static_source_css):
    source_file = os.path.join(static_source_css, css_file)
    dest_file = os.path.join(static_dest_images_path, css_file)
    shutil.copy(source_file, dest_file)

# Copy custom JS folder to the static image
static_source_js = Path(importlib.resources.files("kada_ge_store_plugin") / "static/js")
for js_file in os.listdir(static_source_js):
    source_file = os.path.join(static_source_js, js_file)
    dest_file = os.path.join(static_dest_images_path, js_file)
    shutil.copy(source_file, dest_file)

# Copy webfonts to the static images folder
static_source_webfonts = Path(importlib.resources.files("kada_ge_store_plugin") / "static/webfonts")
for webfont_file in os.listdir(static_source_webfonts):
    source_file = os.path.join(static_source_webfonts, webfont_file)
    dest_file = os.path.join(static_dest_images_path, webfont_file)
    shutil.copy(source_file, dest_file)
