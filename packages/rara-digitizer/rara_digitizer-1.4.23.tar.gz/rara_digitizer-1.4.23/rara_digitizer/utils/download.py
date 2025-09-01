import logging
import os
import zipfile
from pathlib import Path
from urllib.error import ContentTooShortError, HTTPError
from urllib.request import urlretrieve


def retrieve_resource(model_url, model_name, model_path):
    logging.info(f"Downloading model: {model_name}")
    remaining_retries = 4
    while remaining_retries != 0:
        try:
            urlretrieve(model_url, model_path)
            break
        except (ContentTooShortError, HTTPError):
            logging.error(
                f"Failed to download {model_name} from {model_url}. Retrying {remaining_retries} more times!"
            )
            remaining_retries -= 1


def handle_zip(model_name: str, model_path: str, models_dir: str):
    logging.info(f"Unzipping model: {model_name}")
    with zipfile.ZipFile(model_path, "r") as zip_ref:
        zip_ref.extractall(models_dir)
    os.remove(model_path)
    logging.info(f"Model {model_name} unzipped and removed")


def download_model(models: list[str], models_dir: str | Path, models_location: str):
    for model_name in models:
        model_url = models_location + model_name
        model_path = os.path.join(models_dir, model_name)
        if not os.path.exists(model_path) and not os.path.exists(model_path.replace(".zip", "")):
            retrieve_resource(model_url, model_name, model_path)

            if model_path.endswith(".zip"):
                handle_zip(model_name, model_path, models_dir)
