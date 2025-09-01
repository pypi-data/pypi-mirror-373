from typing import Optional

import frogml
from pandas import DataFrame
import onnxruntime as ort
from onnx import ModelProto


class OnnxModel(frogml.FrogMlModel):

    def __init__(self):
        self.model: Optional[ModelProto] = None
        self.inference_session: Optional[ort.InferenceSession] = None
        self.input_names: Optional[list[str]] = None
        self.output_names: Optional[list[str]] = None

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

    def initialize_model(self):
        """
        This method is called on the inference phase to load the model.
        The model is loaded directly from your Repository in Artifactory
        """
        self.model = frogml.onnx.load_model(
            repository="${repositoryKey}",
            model_name="${modelName}",
            version="${modelVersion}",
        )

        # Create an inference session from the loaded model
        self.inference_session = ort.InferenceSession(self.model.SerializeToString())

        # Get input and output names from the model
        self.input_names = [
            output.name for output in self.inference_session.get_outputs()
        ]
        self.output_names = [
            output.name for output in self.inference_session.get_outputs()
        ]

    @frogml.api()
    def predict(self, df: DataFrame) -> DataFrame:
        return df
