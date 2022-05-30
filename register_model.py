import urllib.request

from azureml.core.model import Model

from workspace import get_workspace

MODEL_NAME = "fake_model_onnx"
MODEL_PATH = "fake_model.onnx"


def register_model():
    ws = get_workspace()
    Model.register(ws, model_name=MODEL_NAME, model_path=MODEL_PATH)


if __name__ == '__main__':
    register_model()
