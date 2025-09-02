from frogml.sdk.inner.runtime_di.containers import (
    ContainerLock,
    FrogmlRuntimeContainer,
)


def wire_runtime():
    container = FrogmlRuntimeContainer()
    from frogml.sdk.model import decorators

    container.wire(
        packages=[
            decorators,
        ]
    )
    return container
