from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional, Type

from frogml._proto.qwak.feature_store.sources.streaming_pb2 import (
    CustomDeserializer as ProtoCustomDeserializer,
)
from frogml._proto.qwak.feature_store.sources.streaming_pb2 import (
    Deserialization as ProtoDeserialization,
)
from frogml._proto.qwak.feature_store.sources.streaming_pb2 import (
    GenericDeserializer as ProtoGenericDeserializer,
)
from frogml._proto.qwak.feature_store.sources.streaming_pb2 import (
    MessageFormat as ProtoMessageFormat,
)
from frogml.core.exceptions import FrogmlException


class MessageFormat(Enum):
    JSON = ProtoMessageFormat.JSON
    AVRO = ProtoMessageFormat.AVRO


class Deserializer(ABC):
    @abstractmethod
    def _to_proto(self, artifact_path: Optional[str] = None) -> ProtoDeserialization:
        pass

    @abstractmethod
    def _get_function(self) -> Optional[Callable]:
        pass

    @classmethod
    def _from_proto(
        cls,
        proto_deserializer: ProtoDeserialization,
    ) -> Type["Deserializer"]:
        deserializer = getattr(
            proto_deserializer, proto_deserializer.WhichOneof("type")
        )

        if isinstance(deserializer, ProtoGenericDeserializer):
            return GenericDeserializer._from_proto(proto_deserializer=deserializer)
        elif isinstance(deserializer, ProtoCustomDeserializer):
            return CustomDeserializer._from_proto(proto_deserializer=deserializer)
        else:
            raise FrogmlException(f"Got unsupported deserializer type {deserializer}")


@dataclass
class GenericDeserializer(Deserializer):
    message_format: MessageFormat
    schema: str

    def _to_proto(self, artifact_path: Optional[str] = None) -> ProtoDeserialization:
        # TODO: add backend schema validation
        return ProtoDeserialization(
            generic_deserializer=ProtoGenericDeserializer(
                deserializer_format=self.message_format.value, schema=self.schema
            )
        )

    def _get_function(self) -> Optional[Callable]:
        return None

    @classmethod
    def _from_proto(
        cls, proto_deserializer: ProtoGenericDeserializer
    ) -> Type["GenericDeserializer"]:
        return cls(
            message_format=MessageFormat(proto_deserializer.deserializer_format),
            schema=proto_deserializer.schema,
        )


@dataclass
class CustomDeserializer(Deserializer):
    function: Callable
    _artifact_path: Optional[str] = field(init=False, default=None)

    def _to_proto(self, artifact_path: Optional[str] = None) -> ProtoDeserialization:
        self._validate()

        if artifact_path:
            self._artifact_path = artifact_path

        # TODO: add backend schema validation
        return ProtoDeserialization(
            custom_deserializer=ProtoCustomDeserializer(
                function_name=self.function.__name__, artifact_path=self._artifact_path
            )
        )

    @classmethod
    def _from_proto(
        cls, proto_deserializer: ProtoCustomDeserializer
    ) -> Type["CustomDeserializer"]:
        def dummy_deserializer(df):
            return df

        custom_function: Callable = dummy_deserializer
        custom_function.__name__ = proto_deserializer.function_name

        return cls(function=custom_function)

    def _validate(self):
        if self.function is None:
            raise FrogmlException("deserialization function must be set!")
        if self.function.__name__ == "<lambda>":
            raise FrogmlException("Custom Deserializer can not be set with a lambda")

    def _get_function(self) -> Optional[Callable]:
        return self.function
