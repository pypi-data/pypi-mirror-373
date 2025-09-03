from typing import Any

from frogml.core.exceptions import FrogmlException, FrogmlHTTPException
from frogml.sdk.model.adapters import (
    AutodetectOutputAdapter,
    DataFrameOutputAdapter,
    DefaultOutputAdapter,
    JsonOutputAdapter,
    NumpyOutputAdapter,
    ProtoOutputAdapter,
    TfTensorOutputAdapter,
)
from frogml.sdk.model.base import BaseModel

from .output_adapters.dataframe_output import DataFrameOutput
from .output_adapters.default_output import DefaultOutput
from .output_adapters.json_output import JsonOutput
from .output_adapters.tf_tensor_output import TfTensorOutput


def get_output_adapter(
    model: BaseModel,
):
    adapter = getattr(model.predict, "_output_adapter", "")

    class FrogMLOutput(JsonOutput):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def pack_user_func_return_value(self, return_result: Any) -> Any:
            try:
                return adapter.pack_user_func_return_value(return_result)
            except Exception as e:
                raise FrogmlHTTPException(
                    message=f"Failed to serialize model output. Error is: {e}. For more "
                    f"information please check model logs.",
                    status_code=500,
                )

    class FrogMLOutputWithDefaultFallbackOutput(FrogMLOutput):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def pack_user_func_return_value(self, return_result: Any) -> Any:
            from google.protobuf.message import Message

            first_result = (
                return_result[0]
                if isinstance(return_result, list) and len(return_result) > 0
                else return_result
            )
            if issubclass(type(first_result), Message):
                response = FrogMLOutput().pack_user_func_return_value(return_result)
                return response
            else:
                return DefaultOutput().pack_user_func_return_value(return_result)

    mapping = {
        JsonOutputAdapter: JsonOutput,
        DataFrameOutputAdapter: DataFrameOutput,
        DefaultOutputAdapter: DefaultOutput,
        AutodetectOutputAdapter: FrogMLOutputWithDefaultFallbackOutput,
        ProtoOutputAdapter: FrogMLOutput,
        NumpyOutputAdapter: FrogMLOutput,
        TfTensorOutputAdapter: TfTensorOutput,
    }
    for frogml_impl, runtime_impl in mapping.items():
        if isinstance(adapter, frogml_impl):
            if isinstance(adapter, DataFrameOutputAdapter) and hasattr(
                adapter, "output_orient"
            ):
                return runtime_impl(output_orient=adapter.output_orient)
            return runtime_impl()

    raise FrogmlException("No Adapter selected for output")
