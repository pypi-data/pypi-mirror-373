import dataclasses
from typing import Dict, List, cast

from frogml.core.exceptions import FrogmlException
from frogml.feature_store._common.feature_set_utils import (
    FeatureSetInfo,
    get_entity_type,
    get_typed_feature,
)
from frogml.sdk.model.fs_info_mapping_retriever import retrieve_fs_mapping
from frogml.sdk.model.schema_entities import BaseFeature, Entity, FeatureStoreInput
from frogml.sdk.model.utils.feature_utils import (
    discard_env_from_name,
    extract_env_name,
    extract_featureset_name,
    validate_and_sanitize_features_name,
)


def normalize_features(
    features: List[BaseFeature],
    env_to_feature_sets_infos: Dict[str, Dict[str, FeatureSetInfo]],
) -> List[BaseFeature]:
    """
    Adding the relevant entity to the feature set features
    Args:
        features: list of features
        env_to_feature_sets_infos: dict of environment name to feature set name to it's entity
    return normalize features - the features with the entities
    :param
    """
    new_normalize_features = []
    for feature in features:
        if isinstance(feature, FeatureStoreInput):
            feature_set_env = extract_env_name(feature.name)
            feature_set_name = extract_featureset_name(feature.name)
            feature_set_to_feature_set_info = env_to_feature_sets_infos.get(
                feature_set_env
            )
            if feature_set_to_feature_set_info is None:
                raise FrogmlException(f"Environment '{feature_set_env}' does not exist")
            feature_set_info = feature_set_to_feature_set_info.get(feature_set_name)
            if feature_set_info is None:
                raise FrogmlException(
                    f"Featureset '{feature_set_name}' does not exist in env '{feature_set_env}'"  # noqa
                )
            entity_spec = feature_set_info.entity_spec
            retrieved_entity = Entity(
                name=entity_spec.keys[
                    0
                ],  # currently support only one entity key per feature set
                type=get_entity_type(entity_spec.value_type),
            )
            if (
                feature.entity
                and retrieved_entity.name.lower() != feature.entity.name.lower()
            ):
                raise FrogmlException(
                    f"Explicitly supplied with an invalid entity: {feature.entity}, "
                    f"actual: {retrieved_entity}"
                )
            feature.entity = retrieved_entity
            feature.entity.name = feature.entity.name.lower()
            feature_type = feature_set_info.feature_set_type
            feature_version = feature_set_info.feature_version
            feature_without_env = cast(
                FeatureStoreInput,
                dataclasses.replace(feature, name=discard_env_from_name(feature.name)),
            )
            feature = get_typed_feature(
                feature_without_env, feature_type, feature_version
            )
        new_normalize_features.append(feature)
    return new_normalize_features


def adding_entities_to_schema(entities: List[Entity], features: List[BaseFeature]):
    """
    Adding the new entities for feature store feature to the entities list from schema
    Args:
        entities: list of entities
        features: list of features
    Returns: the entities with the new entities from the feature store features
    """
    entity_name_to_entity = {entity.name: entity for entity in entities}
    for feature in features:
        if isinstance(feature, FeatureStoreInput):
            entity_name_to_entity[feature.entity.name] = feature.entity

    for entity in entity_name_to_entity.values():
        entity.name = entity.name.lower()

    return list(set(entity_name_to_entity.values()))


def normalize_schema(features: List[BaseFeature], entities: List[Entity]):
    """
    validate and sanitize the feature names and entities
    Normalize schema - will add entity to each features in schema if not exists
    Arg:
        model: the model with the required schema
    Return:
        updated model
    """
    sanitized_features = validate_and_sanitize_features_name(features)
    fs_info_cache = retrieve_fs_mapping(sanitized_features)

    normalized_features = normalize_features(sanitized_features, fs_info_cache)
    normalized_entities = adding_entities_to_schema(entities, sanitized_features)

    return normalized_features, normalized_entities


def enrich_schema(features: List[BaseFeature], entities: List[Entity]):
    normalized_features, normalized_entities = normalize_schema(features, entities)
    return normalized_features, normalized_entities
