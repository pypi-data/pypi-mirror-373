from qwak.inner.runtime_di import QwakRuntimeContainer, ContainerLock

from .run_model_locally import run_local


def wire_runtime_with_run_local():
    container = QwakRuntimeContainer()
    from qwak.model import decorators

    container.wire(
        packages=[
            decorators,
        ]
    )
    return container


# Since DI allows overriding containers that are already injected, and there isn't a built-in mechanism to prevent this
# we've added a lock class (singleton) that operates as a lock. Now the production override can lock the container, and
# it will prevent issues where the container is redefined with the basic non production container
if not ContainerLock.locked:
    wire_runtime_with_run_local()

__all__ = ["run_local", "wire_runtime_with_run_local"]
