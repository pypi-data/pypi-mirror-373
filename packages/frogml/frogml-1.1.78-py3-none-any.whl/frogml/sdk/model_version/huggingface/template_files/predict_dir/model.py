from ${path_to_predict_file} import predict as predict_func

import frogml

class HuggingFaceModel(frogml.FrogMlModel):

    def __init__(self):
        self.model = None
        self.tokenizer = None

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

    @frogml.api()
    def predict(self, input_data):
        return predict_func(self.model, input_data, tokenizer=self.tokenizer)