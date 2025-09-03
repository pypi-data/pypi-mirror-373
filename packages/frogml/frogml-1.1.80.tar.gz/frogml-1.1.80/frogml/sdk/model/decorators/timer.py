import contextlib

from dependency_injector.wiring import Provide, inject

from frogml.sdk.inner.runtime_di.containers import FrogmlRuntimeContainer


@inject
@contextlib.contextmanager
def frogml_timer(
    name, create_timer_function=Provide[FrogmlRuntimeContainer.timer_function_creator]
):
    """
    The Frogml timer is a utility for measuring the runtime of ML models, specifically for visibility and latency evaluation.
    It provides a convenient way to measure the time it takes for models to perform predictions
    and to provide a breakdown of the different parts in the production process
    Args:
        name (str): The Frogml timer name. Users may define multiple impl with different names
    """
    return create_timer_function(name)
