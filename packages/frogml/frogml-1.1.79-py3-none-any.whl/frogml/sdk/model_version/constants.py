from strenum import StrEnum

FROGML_LOG_LEVEL_ENVAR_NAME: str = "FROGML_LOG_LEVEL"

CATBOOST_SERIALIZED_TYPE = "cbm"
HUGGINGFACE_FRAMEWORK_FORMAT = "pretrained_model"
ONNX_FRAMEWORK_FORMAT = "onnx"
PYTHON_FRAMEWORK_FORMAT = "pkl"
PYTORCH_FRAMEWORK_FORMAT = "pth"
SCIKIT_LEARN_FRAMEWORK_FORMAT = "joblib"


class ModelFramework(StrEnum):
    CATBOOST = "catboost"
    FILES = "files"
    HUGGINGFACE = "huggingface"
    ONNX = "onnx"
    PYTORCH = "pytorch"
    SCIKIT_LEARN = "scikit_learn"


STORAGE_MODEL_ENTITY_TYPE = "model"
