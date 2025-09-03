from typing import Dict


def _get_model_framework(model_info: Dict) -> str:
    return model_info["model_format"]["framework"]


def _get_model_framework_version(model_info: Dict) -> str:
    return model_info["model_format"]["framework_version"]


def _get_model_serialization_format(model_info: Dict) -> str:
    return model_info["model_format"]["serialization_format"]
