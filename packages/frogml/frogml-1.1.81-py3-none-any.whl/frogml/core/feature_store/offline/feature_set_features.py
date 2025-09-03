from dataclasses import dataclass
from typing import List

from frogml._proto.qwak.offline.serving.v1.feature_values_pb2 import (
    FeaturesetFeatures as ProtoFeaturesetFeatures,
)


@dataclass
class FeatureSetFeatures:
    feature_set_name: str
    feature_names: List[str]

    def to_proto(self) -> ProtoFeaturesetFeatures:
        return ProtoFeaturesetFeatures(
            featureset_name=self.feature_set_name,
            feature_names=self.feature_names,
        )

    @classmethod
    def from_proto(cls, featureset_features_proto: ProtoFeaturesetFeatures):
        return cls(
            feature_set_name=featureset_features_proto.feature_set_name,
            feature_names=featureset_features_proto.feature_names,
        )
