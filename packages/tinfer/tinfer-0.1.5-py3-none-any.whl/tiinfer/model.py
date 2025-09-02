from typing import Dict, List, Union


class Model:
    def __init__(self, model_dir: str = ""):
        self.model_dir = model_dir

    def __call__(self, request: Union[Dict, List]) -> Union[Dict, List]:
        request = self.preprocess(request)
        response = self.predict(request)
        return self.postprocess(response)

    def load(self) -> bool:
        pass

    def preprocess(self, request: Union[Dict, List]) -> Union[Dict, List]:
        return request

    def predict(self, request: Union[Dict, List]) -> Union[Dict, List]:
        return request

    def postprocess(self, request: Union[Dict, List]) -> Union[Dict, List]:
        return request
