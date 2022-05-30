# Minimal reproducible example of Azure ML bug

Steps to reproduce https://github.com/Azure/azure-sdk-for-python/issues/23278.

1. Copy and rename `.env.example` to `.env`. Fill it.

2. Register a fake model: 
   ```
   python register_model.py
   ```

3. To create an inference cluster and deploy the model in it, run: 
   ```
    python deploy.py --env-var-value 1
   ```
   This will:
   - register a new (version of an) Azure ML environment where the environment variable 
     `EXAMPLE_ENV_VAR` is set to the specified value (`1`, in this case). 
   - create an inference cluster if it doesn't exist
   - deploy a service that just returns the value of `EXAMPLE_ENV_VAR` 
     (see `source_dir/entry_script.py`). If the service already exists, the service
     will be updated by running `service.update()`
   - consume the service and print the returned value.

4. Redeploy by setting a different value for the environment variable:
   ```
    python deploy.py --env-var-value 2
   ``` 
   The printed value should now be 2. Nonetheless, it'll still be 1.
