from typing import Optional, Any

import frogml
from frogml import FrogMlModel
from pandas import DataFrame


class ScikitLearnModel(FrogMlModel):

    def __init__(self):
        self.model: Optional[Any] = None

    def build(self) -> None:
        """
        The build() method is called once during the build process.
        Use it for training or actions during the model build phase.
        """
        pass

    def schema(self) -> None:
        """
        schema() define the model input structure, and is used to enforce
        the correct structure of incoming prediction requests.
        """
        pass

    def initialize_model(self) -> None:
        """
        Initialize the scikit-learn model from storage.

        :return: None
        """
        self.model = frogml.scikit_learn.load_model(
            repository="${repositoryKey}",
            model_name="${modelName}",
            version="${modelVersion}",
        )

    @frogml.api()
    def predict(self, df: DataFrame) -> DataFrame:
        return df
