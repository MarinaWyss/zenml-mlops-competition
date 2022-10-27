import yaml

from zenml.integrations.mlflow.mlflow_utils import get_tracking_uri
from zenml.integrations.mlflow.steps import MLFlowDeployerParameters
from zenml.services import load_last_service_from_step
from zenml.integrations.mlflow.steps import mlflow_model_deployer_step
from zenml.integrations.mlflow.model_deployers.mlflow_model_deployer import (
    MLFlowModelDeployer,
)

from steps.import_data import dynamic_importer, import_data
from steps.train_model import train_model
from steps.evaluate_model import evaluate_model
from steps.deploy_model import DeploymentTriggerConfig, deployment_trigger
from steps.inference import (
    MLFlowDeploymentLoaderStepParameters,
    prediction_service_loader,
    predictor
)

from pipelines.deployment_pipeline import continuous_deployment_pipeline
from pipelines.inference_pipeline import inference_pipeline


def run_main(stop_service: bool):
    """Run the mlflow example pipeline"""
    with open('steps/config.yaml', 'r') as file:
        configs = yaml.safe_load(file)

    if stop_service:
        service = load_last_service_from_step(
            pipeline_name="continuous_deployment_pipeline",
            step_name="mlflow_model_deployer_step",
            running=True,
        )
        if service:
            service.stop(timeout=10)
        return

    deployment = continuous_deployment_pipeline(
        import_data=import_data(),
        train_model=train_model(),
        evaluate_model=evaluate_model(),
        deployment_trigger=deployment_trigger(
            config=DeploymentTriggerConfig(
                min_precision=configs['min_precision'],
                min_recall=configs['min_recall']
            )
        ),
        model_deployer=mlflow_model_deployer_step(
            params=MLFlowDeployerParameters(workers=3)
        ),
    )
    deployment.run(config_path='config.yaml')

    inference = inference_pipeline(
        dynamic_importer=dynamic_importer(),
        prediction_service_loader=prediction_service_loader(
            MLFlowDeploymentLoaderStepParameters(
                pipeline_name="continuous_deployment_pipeline",
                step_name="mlflow_model_deployer_step",
            )
        ),
        predictor=predictor(),
    )
    inference.run()

    print(
        "Now run \n "
        f"    mlflow ui --backend-store-uri {get_tracking_uri()}\n"
        "To inspect your experiment runs within the mlflow UI.\n"
        "You can find your runs tracked within the `mlflow_example_pipeline`"
        "experiment. Here you'll also be able to compare the two runs.)"
    )

    model_deployer = MLFlowModelDeployer.get_active_model_deployer()

    # fetch existing services with same pipeline name, step name and model name
    service = model_deployer.find_model_server(
        pipeline_name="continuous_deployment_pipeline",
        pipeline_step_name="mlflow_model_deployer_step",
        running=True,
    )

    if service[0]:
        print(
            f"The MLflow prediction server is running locally as a daemon process "
            f"and accepts inference requests at:\n"
            f"    {service[0].prediction_url}\n"
            f"To stop the service, re-run the same command and supply the "
            f"`--stop-service` argument."
        )


if __name__ == "__main__":
    run_main()
