import requests
from azureml.core import Environment
from azureml.core.webservice import AksWebservice

from deploy import ENVIRONMENT_NAME, SERVICE_NAME
from workspace import get_workspace

ws = get_workspace()

env = Environment.get(ws, ENVIRONMENT_NAME)
print(f"The last registered environment is {env.name}:{env.version}")

service = AksWebservice(ws, SERVICE_NAME)
service_value = requests.post(service.scoring_uri).json()["EXAMPLE_ENV_VAR"]

print("Value of EXAMPLE_ENV_VAR is:")
print("   - in the Azure ML environment:", env.environment_variables['EXAMPLE_ENV_VAR'])
print("   - in the service:", service_value)
