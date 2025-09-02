from .engine import AbstractEngine

__all__ = [
    "inspect",
    "register",
]

REGISTRY: dict[str, AbstractEngine] = {}


def register(engine: AbstractEngine):
    module_name = engine.__module__
    assert module_name not in REGISTRY
    REGISTRY[module_name] = engine


def inspect() -> dict[str, dict]:
    return {module_name: engine.inspect() for module_name, engine in REGISTRY.items()}


def get(job_module_name) -> AbstractEngine:
    return REGISTRY[job_module_name]
