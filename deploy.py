import argparse
import sys

import requests
from azureml.core import Environment, Model, Workspace
from azureml.core.compute import AksCompute
from azureml.core.model import InferenceConfig
from azureml.core.webservice import AksWebservice, LocalWebservice
from azureml.exceptions import ComputeTargetException, WebserviceException

from register_model import MODEL_NAME

CLUSTER_NAME = "temp-cluster"
SERVICE_NAME = "temp-service"
ENVIRONMENT_NAME = "project_environment"


def get_or_create_aks_cluster(
    ws: Workspace,
    cluster_name: str,
) -> AksCompute:
    try:
        target = AksCompute(workspace=ws, name=cluster_name)
        print(f"Found existing compute target with name {cluster_name}. Using it.")
    except ComputeTargetException:
        print(f'Could not find any existing compute target named "{cluster_name}".')
        ans = input("Do you want to provision a new AKS cluster? (y/N) ").lower().strip()
        if ans != "y":
            sys.exit("No compute target was found or created. Deployment canceled.")

        provisioning_config = AksCompute.provisioning_configuration(
            agent_count=1,
            cluster_purpose=AksCompute.ClusterPurpose.DEV_TEST,
            vm_size="STANDARD_A2",
        )
        target = AksCompute.create(ws, cluster_name, provisioning_config)
        target.wait_for_completion(show_output=True)
        print(f'Created a new AKS compute target with name "{cluster_name}"')

    return target


def deploy(ws: Workspace, env_var_value: str, service_name=SERVICE_NAME, local=False) -> None:
    print("Getting the model")
    model = Model(ws, MODEL_NAME)

    # Environment
    env = Environment(name=ENVIRONMENT_NAME)
    env.environment_variables["EXAMPLE_ENV_VAR"] = env_var_value
    print("Registering the environment with EXAMPLE_ENV_VAR =", env_var_value)
    env = env.register(ws)
    print("Environment:", env.name, "version", env.version,
          f"(EXAMPLE_ENV_VAR = {env.environment_variables['EXAMPLE_ENV_VAR']})")

    dummy_inference_config = InferenceConfig(
        environment=env,
        source_directory="./source_dir",
        entry_script="./entry_point.py",
    )

    if local:
        WebserviceClass = LocalWebservice
        deployment_config = LocalWebservice.deploy_configuration(port=4444)
    else:
        WebserviceClass = AksWebservice
        get_or_create_aks_cluster(ws, CLUSTER_NAME)
        deployment_config = AksWebservice.deploy_configuration(
            compute_target_name=CLUSTER_NAME,
            auth_enabled=False,
        )

    try:
        service = WebserviceClass(ws, service_name)
        print(f"The service {service_name} already exists. Updating it.")
        service.update(inference_config=dummy_inference_config)
    except WebserviceException:
        print("The service does not exist. Creating it.")
        service = Model.deploy(
            ws,
            service_name,
            [model],
            dummy_inference_config,
            deployment_config,
        )

    service.wait_for_deployment(show_output=True)

    resp = requests.post(service.scoring_uri, data={"dummy": "dummy"})
    print("Response:", resp.json())


def main():
    from workspace import get_workspace

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env-var-value", help="Set the EXAMPLE_ENV_VAR to this value.", default=1
    )
    args = parser.parse_args()

    ws = get_workspace()
    deploy(ws, args.env_var_value)


if __name__ == '__main__':
    main()
