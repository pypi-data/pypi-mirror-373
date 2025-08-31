from enum import Enum
from typing import Any, Callable


class TemplatedEnum(Enum):
    def __getattribute__(self, name: str) -> Any:
        if name == "value":
            raise AttributeError(
                f"Direct access to '{name}' is not allowed. "
                f"Use '{self.name}.resolved' to get the resolved subject or '{self.name}.template' for the template."
            )
        return super().__getattribute__(name)

    @classmethod
    def __getattr__(cls, name: str) -> Any:
        if name in cls.__members__:
            raise AttributeError(
                f"Direct access to enum member '{name}' is not allowed. "
                f"Use '{name}.resolved' or '{name}.template' to access the subject."
            )
        raise AttributeError(f"'{cls.__name__}' has no attribute '{name}'")

    def __init__(self, *args: Any) -> None:
        # Enum calls __init__ with (cls, *args) where args[0] is the value
        template = args[0] if args else ""
        if not isinstance(template, str):
            raise TypeError(f"Template must be a string, got {type(template)}")
        if not template.strip():
            raise ValueError("Template cannot be empty or whitespace")
        self._template: str = template

    @classmethod
    def set_resolver(cls, resolver: Callable[[str], Any]) -> None:
        if not callable(resolver):
            raise TypeError("Resolver must be callable")

        setattr(cls, "_resolver", resolver)

    @classmethod
    def remove_resolver(cls) -> None:
        """Remove the resolver function from the class."""
        if hasattr(cls, "_resolver"):
            delattr(cls, "_resolver")

    @property
    def template(self) -> str:
        return self._template

    @property
    def resolved(self) -> Any:
        if not hasattr(self.__class__, "_resolver"):
            raise RuntimeError(
                f"Resolver not set for {self.__class__.__name__}. Call set_resolver() first."
            )

        result = self.__class__._resolver(self._template)
        return result

    @property
    def raw_value(self) -> str:
        """Access the raw enum value for debugging purposes."""
        return self._value_

    def __str__(self) -> str:
        try:
            resolved_value = self.resolved
            return str(resolved_value)
        except Exception as e:
            return f"{self.__class__.__name__}.{self.name}[ERROR: {e}]"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"


class NestedTemplatedEnum(TemplatedEnum):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        # Store the nested enum class as a class attribute
        self._nested_enum = None

    @classmethod
    def set_nested_enum(cls, nested_enum_class):
        """Set the nested enum class for this templated enum."""
        cls._nested_enum = nested_enum_class

    @property
    def resolved(self) -> Any:
        if not hasattr(self.__class__, "_resolver"):
            raise RuntimeError(
                f"Resolver not set for {self.__class__.__name__}. Call set_resolver() first."
            )

        # Get the resolved base key from the resolver
        resolved_base = self.__class__._resolver(self._template)

        # Return a simple object that combines the base key with enum values
        class ResolvedNested:
            def __init__(self, base_key: str, enum_class):
                self.base_key = base_key
                self.enum_class = enum_class

            def __getattr__(self, name: str):
                if hasattr(self.enum_class, name):
                    enum_value = getattr(self.enum_class, name)
                    return enum_value
                if name == "value":
                    return self.base_key
                raise AttributeError(
                    f"'{self.enum_class.__name__}' has no attribute '{name}'"
                )

            def __str__(self) -> str:
                return self.base_key

            def __repr__(self) -> str:
                return f"ResolvedNested(base_key='{self.base_key}', enum_class={self.enum_class.__name__})"

        return ResolvedNested(resolved_base, self.__class__._nested_enum)
