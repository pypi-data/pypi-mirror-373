from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from myreze.data import MyrezeDataPackage, Geometry, Time


class Product(ABC):
    """Abstract base class for a store product."""

    def __init__(
        self,
        product_id: str,
        name: str,
        description: str,
        source: str,
        data_types: List[str],
        spatial_coverage: Dict[str, Any],
        temporal_coverage: Dict[str, Any],
        availability: Dict[str, Any],
        visualization_targets: List[str] = None,
        visualization_type: str = "",
    ):
        self.product_id = product_id
        self.name = name
        self.description = description
        self.source = source
        self.data_types = data_types
        self.spatial_coverage = spatial_coverage  # GeoJSON-compatible
        self.temporal_coverage = temporal_coverage  # Time schema
        self.availability = (
            availability  # e.g., {"public": true} or {"users": ["user1"]}
        )
        self.visualization_targets = visualization_targets or [
            "UnrealEngine",
            "ThreeJS",
            "PNG",
        ]
        self.visualization_type = visualization_type

    @abstractmethod
    async def generate_package(
        self,
        spatial_region: Dict[str, Any],
        temporal_region: Dict[str, Any],
        visualization: Optional[Dict[str, Any]] = None,
    ) -> MyrezeDataPackage:
        """Generate a MyrezeDataPackage for the given spatio-temporal region."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert product metadata to a dictionary."""
        return {
            "product_id": self.product_id,
            "name": self.name,
            "description": self.description,
            "source": self.source,
            "data_types": self.data_types,
            "spatial_coverage": self.spatial_coverage,
            "temporal_coverage": self.temporal_coverage,
            "availability": self.availability,
            "visualization_targets": self.visualization_targets,
            "visualization_type": self.visualization_type,
        }
