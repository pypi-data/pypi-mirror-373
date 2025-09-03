from typing import Optional

import frogml
from catboost import CatBoost
from pandas import DataFrame


class CatBoostModel(frogml.FrogMlModel):

    def __init__(self):
        self.model: Optional[CatBoost] = None

    def build(self):
        """
        The build() method is called once during the build process.
        Use it for training or actions during the model build phase.
        """
        pass

    def schema(self):
        """
        schema() define the model input structure, and is used to enforce
        the correct structure of incoming prediction requests.
        """
        pass

    def initialize_model(self) -> None:
        """
        This method is called on the inference phase to load the model.
        The model is loaded directly from your Repository in Artifactory
        """
        self.model = frogml.catboost.load_model(
            repository="${repositoryKey}",
            model_name="${modelName}",
            version="${modelVersion}",
        )

    @frogml.api()
    def predict(self, df: DataFrame) -> DataFrame:
        """
        This method is the live inference method
        """
        return DataFrame(self.model.predict(df))
