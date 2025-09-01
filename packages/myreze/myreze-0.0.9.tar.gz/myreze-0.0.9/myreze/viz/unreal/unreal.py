from typing import Dict, Type, Optional, Any
from abc import ABC, abstractmethod


class UnrealRenderer(ABC):
    """
    Unreal Engine-specific rendering utilities..
    """

    # Registry to keep track of all renderer subclasses
    _registry: Dict[str, Type["UnrealRenderer"]] = {}

    def __init__(self):
        pass

    @abstractmethod
    def render(
        self, data: "MyrezeDataPackage", params: Optional[Dict[str, Any]] = None
    ) -> str:
        """Render the data package as a Unreal Engine object."""
        pass

    def to_dict(self) -> dict:
        """Convert the renderer to a dictionary."""
        return {
            "type": self.__class__.__name__,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UnrealRenderer":
        """Create a renderer from a dictionary."""
        renderer_type = data.get("type")
        if not renderer_type:
            raise ValueError("Missing 'type' field in renderer data")

        # Get the appropriate subclass from the registry
        renderer_class = cls._registry.get(renderer_type)
        if not renderer_class:
            raise ValueError(f"Unknown renderer type: {renderer_type}")

        # Create and return an instance of the appropriate subclass
        return renderer_class()

    @classmethod
    def register(cls, renderer_class: Type["UnrealRenderer"]) -> Type["UnrealRenderer"]:
        """Register a renderer subclass."""
        cls._registry[renderer_class.__name__] = renderer_class
        return renderer_class
