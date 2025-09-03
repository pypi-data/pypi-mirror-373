from typing import Any, Optional, Sequence

from .base_input_adapter import BaseInputAdapter


class DataFrameInputAdapter(BaseInputAdapter):
    def __init__(self, input_orient: Optional[str] = None):
        self.input_orient = input_orient

    def extract_user_func_arg(self, data: str) -> Sequence[Any]:
        pass
