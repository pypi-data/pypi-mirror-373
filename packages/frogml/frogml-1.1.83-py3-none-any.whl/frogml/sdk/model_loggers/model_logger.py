import os
import pickle  # nosec B403
import tempfile

from frogml.sdk.model.base import BaseModel

from frogml.core.model_loggers.artifact_logger import load_file, log_file

MODEL_TAG = "frogml_model"
FILE_NAME = "frogml_model.pkl"


def log_model(build_id: str, model: BaseModel) -> None:
    with open(FILE_NAME, "wb") as handle:
        pickle.dump(model, handle, protocol=pickle.HIGHEST_PROTOCOL)

    log_file(from_path=FILE_NAME, tag=MODEL_TAG, build_id=build_id, model_id=None)


def load_model(model_id: str, build_id: str) -> BaseModel:
    with tempfile.TemporaryDirectory() as td:
        temp_file_path = os.path.join(td, FILE_NAME)
        load_file(
            to_path=temp_file_path, tag=MODEL_TAG, build_id=build_id, model_id=model_id
        )

        with open(temp_file_path, "rb") as handle:
            model = pickle.load(handle)  # nosec B301

    return model
