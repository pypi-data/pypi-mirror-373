from typing import Any

from .base_output_adapter import BaseOutputAdapter


class DataFrameOutputAdapter(BaseOutputAdapter):
    def __init__(self, output_orient: str = "records"):
        self.output_orient = output_orient

    @staticmethod
    def pack_user_func_return_value(return_result: Any) -> str:
        pass
