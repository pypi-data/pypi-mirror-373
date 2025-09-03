## kada-gx-plugin

kada-gx-plugin generates validation results in a format for loading into the K Platform.

Plugin has been tested for only Great Expectations versions `1.0.x - 1.1.x`.

Results will continue to be written to existing default validation stores, any additional actions defined for a Checkpoint is considered additional steps and does not overwrite existing steps.

### Steps to use the KadaStoreValidationResultsAction from the plugin

1. Install the plugin by `pip install kada-gx-plugin` to write to a local filesystem or `pip install kada-gx-plugin[azure]` to write to an Azure blob store. Additional azure dependencies will be required.

2. Import the Checkpoint class from the plugin as there are patches made to the default class to ensure the plugin is compatible.

>#### Import Checkpoint and KadaStoreValidationResultsAction
```python
    from kada_ge_store_plugin.kada_store_validation import KadaStoreValidationResultsAction, Checkpoint
```

3. In your required `checkpoint`, add the following action to your checkpoint actions when defining a checkpoint. `AZURE_BLOB_SAS_URL` is the container SAS token which is provided by KADA. `prefix` should be updated to the landing folder found in K Platform Source onboarding.

>#### Checkpoint action for writing to local filesystem
```python
    checkpoint_action_list = [
        KadaStoreValidationResultsAction(
            name='this can be any name',
            prefix='my-path/inside/test-results-directory',
            test_directory='/tmp/test-results-directory
        )
    ]
```
This will write validation result files to /tmp/test-results-directory/my-path/inside/test-results-directory

>#### Checkpoint action for writing to Azure blob store

```python
    checkpoint_action_list = [
        KadaStoreValidationResultsAction(
            name='this can be any name',
            prefix='my-path/inside/test-results-directory',
            azure_blob_sas_url='${AZURE_BLOB_SAS_URL}'
        )
    ]
```

4. Define the variable `AZURE_BLOB_SAS_URL`. In `uncommited/config_variables.yml` add the variable `AZURE_BLOB_SAS_URL: <SAS url blob >` or alternatively set `AZURE_BLOB_SAS_URL` in the environment variables. OR alternatively if you using a codified approach just define it as a standard python varaible and change the definition like so

```python
    checkpoint_action_list = [
        KadaStoreValidationResultsAction(
            name='this can be any name',
            prefix='my-path/inside/test-results-directory',
            azure_blob_sas_url=AZURE_BLOB_SAS_URL
        )
    ]
```