from typing import Optional, Any

import frogml
from pandas import DataFrame
import torch


class PytorchModel(frogml.FrogMlModel):

    def __init__(self):
        self.model: Optional[Any] = None
        self.device: Optional[torch.device] = None

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
        This method is called on the inference phase to load the model.
        The model is loaded directly from your Repository in Artifactory

        :return: None
        """
        self.model = frogml.pytorch.load_model(
            repository="${repositoryKey}",
            model_name="${modelName}",
            version="${modelVersion}",
        )
        # Check if a GPU is available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        # Set model to evaluation mode
        self.model.eval()

    @frogml.api()
    def predict(self, df: DataFrame) -> DataFrame:
        return df
