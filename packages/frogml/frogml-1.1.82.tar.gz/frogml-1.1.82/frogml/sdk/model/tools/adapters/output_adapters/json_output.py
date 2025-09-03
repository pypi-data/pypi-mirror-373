import json
from typing import Any

from frogml.core.exceptions import FrogmlHTTPException
from frogml.sdk.model.tools.adapters.encoders import NumpyJsonEncoder

from .base_output import BaseOutputAdapter


class JsonOutput(BaseOutputAdapter):
    def pack_user_func_return_value(self, return_result: Any) -> str:
        try:
            return json.dumps(return_result, cls=NumpyJsonEncoder, ensure_ascii=False)
        except AssertionError as e:
            FrogmlHTTPException(400, message=str(e))
        except Exception as e:
            FrogmlHTTPException(500, message=str(e))
