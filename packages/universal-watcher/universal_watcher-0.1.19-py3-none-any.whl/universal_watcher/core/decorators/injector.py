import inspect
from functools import wraps
from typing import get_type_hints
import threading


class CircularDependencyError(Exception):
    """Custom exception for circular dependencies."""


class DependencyInjector:
    _singleton_attribute = "_di_inject_as_singleton"
    _dependency_stack = []
    _singletons = {}
    _lock = threading.RLock()

    @classmethod
    def inject_as_singleton(cls, target_cls):
        """Mark a class as a singleton.

        Args:
            target_cls (type): The class to be marked as a singleton.

        Returns:
            type: The original class marked as singleton.
        """
        setattr(target_cls, cls._singleton_attribute, True)
        return target_cls

    @classmethod
    def _get_dependency_instance(cls, dependency_cls):
        """Retrieve an instance of the specified dependency.

        Args:
            dependency_cls (type): The dependency class to instantiate.

        Raises:
            CircularDependencyError: If a circular dependency is detected.

        Returns:
            object: An instance of the dependency class.
        """
        with cls._lock:
            if dependency_cls in cls._dependency_stack:
                cycle = " -> ".join(
                    [c.__name__ for c in cls._dependency_stack]
                    + [dependency_cls.__name__]
                )
                raise CircularDependencyError(
                    f"Circular dependency detected: {cycle}"
                )

            cls._dependency_stack.append(dependency_cls)

            is_singleton = getattr(
                dependency_cls, cls._singleton_attribute, False
            )
            if is_singleton:
                if dependency_cls not in cls._singletons:
                    cls._singletons[dependency_cls] = dependency_cls()
                dependency = cls._singletons[dependency_cls]
            else:
                dependency = dependency_cls()
            cls._dependency_stack.pop()

            return dependency

    @classmethod
    def _get_init_type_hints(cls, target_cls, original_init):
        """Retrieve type hints from the target class's constructor.

        Args:
            target_cls (type): The class whose constructor to inspect.
            original_init (Callable): The original __init__ method of the class.

        Raises:
            ValueError: If the module for target_cls cannot be determined.

        Returns:
            dict: A dictionary of parameter names to their type hints.
        """
        module = inspect.getmodule(target_cls)
        if module is None:
            raise ValueError(f"Cannot determine the module for {target_cls}")

        return get_type_hints(
            original_init, globalns=module.__dict__, localns={}
        )

    @classmethod
    def inject_dependencies(cls, target_cls):
        """Inject dependencies into the target class's constructor.

        Args:
            target_cls (type): The class into which dependencies will be injected.

        Raises:
            ValueError: If a required dependency's type hint is missing or incomplete.

        Returns:
            type: The original class with dependencies injected.
        """
        original_init = target_cls.__init__

        @wraps(original_init)
        def new_init(self, *args, **kwargs):
            type_hints = cls._get_init_type_hints(target_cls, original_init)
            params = inspect.signature(original_init).parameters

            for name, param in params.items():
                if (
                    name == "self"
                    or name in kwargs
                    or param.default is not param.empty
                ):
                    continue

                if param.annotation == param.empty:
                    raise ValueError(
                        f"Missing the type of required dependency: {name}"
                    )

                dependency_cls = type_hints.get(param.name)
                if not dependency_cls:
                    raise ValueError(
                        f"Type hint for '{param.name}' not found."
                    )

                kwargs[name] = cls._get_dependency_instance(dependency_cls)

            original_init(self, *args, **kwargs)

        target_cls.__init__ = new_init
        return target_cls
