import os

import dotenv
from azureml.core import Workspace
from azureml.core.authentication import InteractiveLoginAuthentication

dotenv.load_dotenv()


def get_workspace():
    return Workspace.get(
        name=os.getenv("WORKSPACE_NAME"),
        subscription_id=os.getenv("SUBSCRIPTION_ID"),
        resource_group=os.getenv("RESOURCE_GROUP"),
        auth=InteractiveLoginAuthentication(
            tenant_id=os.getenv("TENANT_ID")
        ),
    )
