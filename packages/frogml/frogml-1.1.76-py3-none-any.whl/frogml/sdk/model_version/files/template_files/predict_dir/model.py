from pathlib import Path
from typing import Optional

from ${path_to_predict_file} import predict as predict_func

import frogml


class FilesModel(frogml.FrogMlModel):

    def __init__(self):
        self.model_file_path: Optional[Path] = None

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
        self.model_file_path: Path = frogml.files.load_model(
            repository="${repositoryKey}",
            model_name="${modelName}",
            version="${modelVersion}",
        )

    @frogml.api()
    def predict(self, input_data):
        return predict_func(self.model_file_path, input_data)
