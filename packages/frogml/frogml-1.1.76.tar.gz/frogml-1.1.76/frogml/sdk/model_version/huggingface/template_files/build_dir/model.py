from typing import Optional

import frogml
from pandas import DataFrame
import torch
from transformers import PreTrainedModel, PreTrainedTokenizer


class HuggingFaceModel(frogml.FrogMlModel):

    def __init__(self):
        self.model: Optional[PreTrainedModel] = None
        self.tokenizer: Optional[PreTrainedTokenizer] = None
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
        Initialize the HuggingFace model and tokenizer.
        """
        self.model, self.tokenizer = frogml.huggingface.load_model(
            repository="${repositoryKey}",
            model_name="${modelName}",
            version="${modelVersion}",
        )
        # Check if a GPU is available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    @frogml.api()
    def predict(self, df: DataFrame) -> DataFrame:
        return df
