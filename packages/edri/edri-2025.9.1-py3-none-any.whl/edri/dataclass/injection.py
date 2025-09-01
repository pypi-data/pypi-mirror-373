from inspect import signature
from typing import Any, Type


class Injection:
    """
    A class that facilitates the injection of dependencies into one or more classes.
    It manages the initialization of multiple classes by providing their necessary parameters.

    This class iterates over provided classes and dynamically creates callables that can instantiate
    each class with filtered parameters based on the provided arguments.

    Args:
        classes (tuple[Type]): A tuple of class types to be instantiated.
        parameters (dict[str, Any]): A dictionary of parameter names and values that will be passed to
                                     the constructors of the classes. Only parameters matching the
                                     constructor's signature will be passed to the class.

    Methods:
        __iter__: Iterates over the provided classes and creates callables that can instantiate them
                  with the appropriate parameters.
        __repr__: Returns a string representation of the Injection instance, showing the classes and
                  the parameters that will be passed to their constructors.
    """

    def __init__(self, classes: tuple[Type], parameters: dict[str, Any]):
        super().__init__()
        self.classes = classes  # Store the classes
        self.parameters = parameters  # Store the parameters

    def __iter__(self):
        # Create the callable on demand when iterating
        for cls in self.classes:
            # Get the signature of the __init__ method of the class
            sig = signature(cls)
            # Extract parameter names from the signature
            param_names: list[str] = [param.name for param in sig.parameters.values() if param.name != 'self']

            # Filter the parameters dictionary to include only the ones needed for the class
            filtered_params: dict[str, Any] = {k: v for k, v in self.parameters.items() if k in param_names}

            # Create the callable (function) to instantiate the class with the filtered parameters
            def create_instance(value: str, cls=cls, filtered_params=filtered_params):
                # Here we assume that `value` will be passed to the `__init__` of the class
                # This is a simple way to make sure that `value` can be used along with the filtered params
                return cls(value, **filtered_params)

            # Yield the callable (this will be used in the iteration)
            yield create_instance

    def __repr__(self):
        # Representation of the class, including class names and their filtered parameters
        param_info = []
        for cls in self.classes:
            # Get the signature of the __init__ method of the class
            sig = signature(cls)
            # Extract parameter names from the signature
            param_names: list[str] = [param.name for param in sig.parameters.values() if param.name != 'self']

            # Filter the parameters dictionary to include only the ones needed for the class
            filtered_params: dict[str, Any] = {k: v for k, v in self.parameters.items() if k in param_names}

            param_info.append(f"{cls.__name__}({', '.join([f'{k}={v}' for k, v in filtered_params.items()])})")

        # Return a string with the class names and their parameters
        return f"Injection[{', '.join(param_info)}]"
