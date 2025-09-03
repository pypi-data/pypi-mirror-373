from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Type

from frogml._proto.qwak.build.v1.build_pb2 import BatchFeatureV1 as ProtoBatchFeatureV1
from frogml._proto.qwak.build.v1.build_pb2 import Entity as ProtoEntity
from frogml._proto.qwak.build.v1.build_pb2 import (
    ExplicitFeature as ProtoExplicitFeature,
)
from frogml._proto.qwak.build.v1.build_pb2 import Feature as ProtoFeature
from frogml._proto.qwak.build.v1.build_pb2 import (
    InferenceOutput as ProtoInferenceOutput,
)
from frogml._proto.qwak.build.v1.build_pb2 import Prediction as ProtoPrediction
from frogml._proto.qwak.build.v1.build_pb2 import RequestInput as ProtoRequestInput
from frogml._proto.qwak.build.v1.build_pb2 import ValueType


@dataclass(unsafe_hash=True)
class Entity:
    name: str
    type: Type = str

    def to_proto(self):
        return ProtoEntity(
            name=self.name, type=ValueType(type=_type_conversion(self.type))
        )


@dataclass
class BaseFeature(ABC):
    name: str

    @abstractmethod
    def to_proto(self):
        pass


@dataclass(unsafe_hash=True)
class ExplicitFeature(BaseFeature):
    type: Type

    def to_proto(self):
        return ProtoFeature(
            explicit_feature=ProtoExplicitFeature(
                name=self.name, type=ValueType(type=_type_conversion(self.type))
            )
        )


@dataclass(unsafe_hash=True)
class RequestInput(BaseFeature):
    type: Type

    def to_proto(self):
        return ProtoFeature(
            request_input=ProtoRequestInput(
                name=self.name, type=ValueType(type=_type_conversion(self.type))
            )
        )


@dataclass(unsafe_hash=True)
class FeatureStoreInput(BaseFeature):
    entity: Optional[Entity] = None

    def to_proto(self):
        return ProtoFeature(
            batch_feature_v1=ProtoBatchFeatureV1(
                name=self.name, entity=self.entity.to_proto() if self.entity else None
            )
        )


@dataclass(unsafe_hash=True)
class InferenceOutput:
    name: str
    type: type

    def to_proto(self):
        return ProtoInferenceOutput(
            name=self.name, type=ValueType(type=_type_conversion(self.type))
        )


@dataclass(unsafe_hash=True)
class Prediction:
    name: str
    type: type

    def to_proto(self):
        return ProtoPrediction(
            name=self.name, type=ValueType(type=_type_conversion(self.type))
        )


def _type_conversion(type):
    if type == int:
        return ValueType.INT32
    elif type == str:
        return ValueType.STRING
    elif type == bytes:
        return ValueType.BYTES
    elif type == bool:
        return ValueType.BOOL
    elif type == float:
        return ValueType.FLOAT
