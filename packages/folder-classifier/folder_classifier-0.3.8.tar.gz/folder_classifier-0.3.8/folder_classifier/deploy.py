from ray.serve import Application

from folder_classifier.app import FolderClassifierAPI
from folder_classifier.dto import AppConfig


def build_app(args: AppConfig) -> Application:
    assert args and args.model, "AppConfig model is required"
    assert args.model.app_name and args.model.deployment, "Model's app_name and deployment are required"

    app = FolderClassifierAPI.bind(args.model)
    return app
