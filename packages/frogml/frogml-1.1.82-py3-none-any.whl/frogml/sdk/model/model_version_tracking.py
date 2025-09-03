from typing import Dict, Union

from frogml.core.inner.singleton_meta import SingletonMeta


class FrogmlModelVersionTracking(metaclass=SingletonMeta):
    def __init__(self):
        self.metric: Dict[str, Union[int, str]] = {}
        self.param: Dict[str, Union[int, str]] = {}

    def log_param(self, params: Dict[str, Union[int, str]]):
        self.param = {**self.param, **params}

    def log_params(self, params: Dict[str, Union[int, str]]):
        self.log_param(params)

    def log_metric(self, metrics: Dict[str, Union[int, str]]):
        self.metric = {**self.metric, **metrics}

    def log_metrics(self, metrics: Dict[str, Union[int, str]]):
        self.log_metric(metrics)

    def get_metrics(self) -> Dict[str, Union[int, str]]:
        return self.metric

    def get_params(self) -> Dict[str, Union[int, str]]:
        return self.param


def log_metric(metrics):
    client = FrogmlModelVersionTracking()
    client.log_metric(metrics)


def log_param(params):
    client = FrogmlModelVersionTracking()
    client.log_param(params)


def log_metrics(metrics):
    client = FrogmlModelVersionTracking()
    client.log_metric(metrics)


def log_params(params):
    client = FrogmlModelVersionTracking()
    client.log_param(params)


def get_params():
    client = FrogmlModelVersionTracking()
    return client.get_params()


def get_metrics():
    client = FrogmlModelVersionTracking()
    return client.get_metrics()
