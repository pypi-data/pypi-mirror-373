import time
from dataclasses import dataclass
from typing import Dict, Optional

from frogml._proto.qwak.build.v1.build_pb2 import BatchFeature as ProtoBatchFeature
from frogml._proto.qwak.build.v1.build_pb2 import BatchFeatureV1 as ProtoBatchFeatureV1
from frogml._proto.qwak.build.v1.build_pb2 import Feature as ProtoFeature
from frogml._proto.qwak.build.v1.build_pb2 import (
    StreamingAggregationFeature as ProtoStreamingAggregationFeature,
)
from frogml._proto.qwak.build.v1.build_pb2 import (
    StreamingFeature as ProtoStreamingFeature,
)
from frogml._proto.qwak.build.v1.build_pb2 import (
    StreamingFeatureV1 as ProtoStreamingFeatureV1,
)
from frogml._proto.qwak.feature_store.entities.entity_pb2 import (
    EntitySpec as ProtoEntitySpec,
)
from frogml._proto.qwak.feature_store.features.feature_set_types_pb2 import (
    BatchFeatureSet as ProtoBatchFeatureSet,
)
from frogml._proto.qwak.feature_store.features.feature_set_types_pb2 import (
    BatchFeatureSetV1 as ProtoBatchFeatureSetV1,
)
from frogml._proto.qwak.feature_store.features.feature_set_types_pb2 import (
    FeatureSetType as ProtoFeatureSetType,
)
from frogml._proto.qwak.feature_store.features.feature_set_types_pb2 import (
    StreamingAggregationFeatureSet as ProtoStreamingAggregationFeatureSet,
)
from frogml._proto.qwak.feature_store.features.feature_set_types_pb2 import (
    StreamingFeatureSetV1 as ProtoStreamingFeatureSetV1,
)
from frogml.core.clients.feature_store import FeatureRegistryClient
from frogml.core.exceptions import FrogmlException
from frogml.sdk.model.schema_entities import BaseFeature, Entity, FeatureStoreInput

_INTERNAL_KEY_PREFIX: str = "_frogml_key_"


@dataclass(unsafe_hash=True)
class BatchFeature(BaseFeature):
    entity: Optional[Entity] = None

    def to_proto(self):
        return ProtoFeature(
            batch_feature=ProtoBatchFeature(
                name=self.name, entity=self.entity.to_proto()
            )
        )


@dataclass(unsafe_hash=True)
class BatchFeatureV1(BaseFeature):
    entity: Optional[Entity] = None

    def to_proto(self):
        return ProtoFeature(
            batch_feature_v1=ProtoBatchFeatureV1(
                name=self.name, entity=self.entity.to_proto()
            )
        )


@dataclass(unsafe_hash=True)
class StreamingFeature(BaseFeature):
    entity: Entity

    def to_proto(self):
        return ProtoFeature(
            streaming_feature=ProtoStreamingFeature(
                name=self.name, entity=self.entity.to_proto()
            )
        )


@dataclass(unsafe_hash=True)
class StreamingFeatureV1(BaseFeature):
    entity: Optional[Entity] = None

    def to_proto(self):
        return ProtoFeature(
            streaming_feature_v1=ProtoStreamingFeatureV1(
                name=self.name, entity=self.entity.to_proto()
            )
        )


@dataclass(unsafe_hash=True)
class StreamingAggregationFeature(BaseFeature):
    entity: Optional[Entity] = None

    def to_proto(self):
        return ProtoFeature(
            streaming_aggregation_feature=ProtoStreamingAggregationFeature(
                name=self.name, entity=self.entity.to_proto()
            )
        )


@dataclass()
class FeatureSetInfo:
    entity_spec: ProtoEntitySpec
    feature_set_type: ProtoFeatureSetType
    feature_version: int


def get_feature_set_info(
    feature_manager_client: FeatureRegistryClient, feature_set_name: str
) -> FeatureSetInfo:
    """
    Get the entities by the feature set name and feature type
    Args:
        feature_manager_client: feature manager client for the grpc request
        feature_set_name: the required feature set name
    Returns: tuple of entity spec, type and feature version

    """
    feature_set_response = feature_manager_client.get_feature_set_by_name(
        feature_set_name
    )
    if not feature_set_response:
        raise FrogmlException(f"Featureset '{feature_set_name}' does not exist")

    featureset_type: ProtoFeatureSetType = get_feature_type(
        feature_set_response.feature_set.feature_set_definition.feature_set_spec.feature_set_type
    )
    featureset_version = _get_featureset_version(featureset_type)

    return FeatureSetInfo(
        entity_spec=feature_set_response.feature_set.feature_set_definition.feature_set_spec.entity.entity_spec,
        feature_set_type=featureset_type,
        feature_version=featureset_version,
    )


def get_feature_type(feature_set_type: ProtoFeatureSetType):
    return getattr(feature_set_type, feature_set_type.WhichOneof("set_type"))


def _get_featureset_version(feature_set_type: ProtoFeatureSetType) -> int:
    """
    Get Featureset version. Return 0 if none version is set
    """
    if hasattr(feature_set_type, "qwak_internal_protocol_version"):
        return feature_set_type.qwak_internal_protocol_version
    return 0


def get_typed_feature(
    feature: FeatureStoreInput,
    feature_type: ProtoFeatureSetType,
    featureset_version: int,
) -> BaseFeature:
    """
    convert InputFeature to the relevant type
    Args:
        feature: Input feature to cast to the correct type
        feature_type: the feature type as it registered
        featureset_version: the version of the featureset

    Return:
        BaseFeature with the correct type
    """
    if isinstance(feature_type, ProtoBatchFeatureSet):
        return BatchFeature(name=feature.name, entity=feature.entity)
    elif isinstance(feature_type, ProtoBatchFeatureSetV1) and featureset_version == 0:
        return BatchFeature(name=feature.name, entity=feature.entity)
    elif isinstance(feature_type, ProtoBatchFeatureSetV1) and featureset_version != 0:
        return BatchFeatureV1(name=feature.name, entity=feature.entity)
    elif (
        isinstance(feature_type, ProtoStreamingFeatureSetV1) and featureset_version == 0
    ):
        return StreamingFeature(name=feature.name, entity=feature.entity)
    elif (
        isinstance(feature_type, ProtoStreamingFeatureSetV1) and featureset_version != 0
    ):
        return StreamingFeatureV1(name=feature.name, entity=feature.entity)
    elif isinstance(feature_type, ProtoStreamingAggregationFeatureSet):
        return StreamingAggregationFeature(name=feature.name, entity=feature.entity)
    else:
        raise ValueError(
            f"Feature set type {feature_type} with protocol version {featureset_version} is not supported for extraction"
        )


def get_env_to_featuresets_mapping(
    feature_manager_client: FeatureRegistryClient,
) -> Dict[str, Dict[str, FeatureSetInfo]]:
    """
    Get mapping of the account's environment name to feature sets and converts each FeatureSet to FeatureSetInfo
    :param feature_manager_client:
    :return: Dict[str, List[FeatureSetInfo]] where the key is the environment name and the value is a list of FeatureSetInfo
    """
    env_to_featuresets_mapping = feature_manager_client.get_env_to_featuresets_mapping()

    # Convert the mapping to a dictionary of type Dict[str, List[FeatureSetInfo]]
    result = {}
    for (
        env_name,
        feature_sets_infos,
    ) in env_to_featuresets_mapping.env_to_feature_set_mapping.items():
        env_name = env_name.lower()
        result[env_name] = {}
        for feature_set in feature_sets_infos.feature_sets:
            featureset_type: ProtoFeatureSetType = get_feature_type(
                feature_set.feature_set_definition.feature_set_spec.feature_set_type
            )
            featureset_version = _get_featureset_version(featureset_type)

            feature_set_info = FeatureSetInfo(
                entity_spec=feature_set.feature_set_definition.feature_set_spec.entity.entity_spec,
                feature_set_type=featureset_type,
                feature_version=featureset_version,
            )

            feature_set_name = (
                feature_set.feature_set_definition.feature_set_spec.name.lower()
            )
            result[env_name][feature_set_name] = feature_set_info
    return result


def get_entity_type(value_type: ProtoEntitySpec.ValueType):
    """
    Normalize entity by the enum
    """

    if value_type == ProtoEntitySpec.ValueType.STRING:
        return str
    elif value_type == ProtoEntitySpec.ValueType.INT:
        return int


def generate_key_unique_name(featureset_name: str):
    """
    Generate a name for the feature set key to be registered or treated as a Frogml entity based on its' featuresets'
    name
    """
    return f"{_INTERNAL_KEY_PREFIX}_{featureset_name}_{round(time.time() * 1000)}"


def get_batch_source_for_featureset(
    batch_ds_name: str, feature_registry: FeatureRegistryClient
):
    batch_ds = feature_registry.get_data_source_by_name(batch_ds_name)
    if not batch_ds:
        raise FrogmlException(
            f"Trying to register a feature set with a non registered data source -: {batch_ds_name}"
        )

    ds_spec = batch_ds.data_source.data_source_definition.data_source_spec

    if ds_spec.WhichOneof("type") != "batch_source":
        raise ValueError(
            f"Can only register streaming backfill/batch featuresets with batch sources. "
            f"Source {batch_ds_name} is of type {ds_spec.WhichOneof('type')}"
        )

    return ds_spec.batch_source
