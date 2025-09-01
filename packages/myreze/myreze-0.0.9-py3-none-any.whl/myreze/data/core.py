from typing import Dict, Any, Optional, Union, List, Literal
import json
import numpy as np
from myreze.viz.threejs.threejs import ThreeJSRenderer
from myreze.viz.unreal.unreal import UnrealRenderer
from myreze.data.validate import validate_mdp
import isodate  # For ISO 8601 parsing
import base64
import hashlib
from datetime import datetime
import warnings

# Forward declaration to avoid circular imports
MultiAgentContext = None

# Constants for LLM agent discovery
VISUALIZATION_TYPES = [
    "flat_overlay",
    "point_cloud",
    "heatmap",
    "vector_field",
    "terrain",
    "trajectory",
    "contour",
    "png_overlay",
    "animated_overlay",
    "point_data_svg",
    "map_tile",
]

TIME_TYPES = ["Timestamp", "Span", "Series"]

# Enhanced semantic categories for MCP/RAG integration
SEMANTIC_CATEGORIES = [
    "weather",
    "climate",
    "environmental",
    "atmospheric",
    "oceanic",
    "terrestrial",
    "urban",
    "transportation",
    "geological",
    "hydrological",
    "biological",
    "agricultural",
    "energy",
    "infrastructure",
    "demographic",
    "economic",
]

# Data structure schemas for each visualization type
VISUALIZATION_SCHEMAS = {
    "flat_overlay": {
        "required_fields": ["grid", "bounds"],
        "optional_fields": ["resolution", "units", "colormap"],
        "grid_format": "2D numpy array or nested list",
        "bounds_format": "[west, south, east, north] in degrees",
        "description": "2D map overlays like weather maps, satellite imagery",
    },
    "point_cloud": {
        "required_fields": ["locations", "values"],
        "optional_fields": ["point_ids", "colors", "sizes"],
        "locations_format": ("[{lat: float, lon: float, elevation?: float}, ...]"),
        "values_format": "List of measurement values at each location",
        "description": ("Discrete data points like sensor readings, weather stations"),
    },
    "heatmap": {
        "required_fields": ["grid", "bounds"],
        "optional_fields": ["values_range", "colormap", "opacity"],
        "grid_format": "2D numpy array with continuous values",
        "bounds_format": "[west, south, east, north] in degrees",
        "description": "Continuous surfaces like temperature, pressure fields",
    },
    "vector_field": {
        "required_fields": ["grid_points", "u_component", "v_component"],
        "optional_fields": ["magnitude", "arrow_scale", "color_by"],
        "grid_points_format": "{lats: [...], lons: [...]}",
        "components_format": "2D arrays for east-west (u) and north-south (v)",
        "description": "Directional data like wind, ocean currents",
    },
    "map_tile": {
        "required_fields": "Either ['grid', 'bounds'] OR ['png_bytes', 'bounds']",
        "optional_fields": ["crs", "colormap", "nodata", "vmin", "vmax"],
        "grid_format": "2D numpy array with scalar values",
        "png_bytes_format": "Base64-encoded PNG string or raw bytes (supports grayscale, RGB, RGBA)",
        "bounds_format": "[west, south, east, north] in degrees or meters",
        "crs_format": "EPSG:4326 (WGS84) or EPSG:3857 (Web Mercator)",
        "description": "XYZ map tiles for web mapping services (Google Maps, OpenStreetMap style)",
    },
}


class VisualSummary:
    """
    Container for visual representations that multimodal LLMs can interpret.

    This class encapsulates various visual formats of the data including
    thumbnails, previews, and visual fingerprints for content-based analysis.
    """

    def __init__(
        self,
        thumbnail_png: Optional[bytes] = None,
        preview_svg: Optional[str] = None,
        visual_hash: Optional[str] = None,
        color_palette: Optional[List[str]] = None,
        visual_stats: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize visual summary.

        Args:
            thumbnail_png: Small PNG thumbnail (base64 encoded when serialized)
            preview_svg: SVG preview for vector representation
            visual_hash: Content-based hash for similarity detection
            color_palette: Dominant colors in the visualization
            visual_stats: Statistical summary of visual properties
        """
        self.thumbnail_png = thumbnail_png
        self.preview_svg = preview_svg
        self.visual_hash = visual_hash
        self.color_palette = color_palette or []
        self.visual_stats = visual_stats or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "thumbnail_png_base64": (
                base64.b64encode(self.thumbnail_png).decode("utf-8")
                if self.thumbnail_png
                else None
            ),
            "preview_svg": self.preview_svg,
            "visual_hash": self.visual_hash,
            "color_palette": self.color_palette,
            "visual_stats": self.visual_stats,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VisualSummary":
        """Create from dictionary."""
        thumbnail_png = None
        if data.get("thumbnail_png_base64"):
            thumbnail_png = base64.b64decode(data["thumbnail_png_base64"])

        return cls(
            thumbnail_png=thumbnail_png,
            preview_svg=data.get("preview_svg"),
            visual_hash=data.get("visual_hash"),
            color_palette=data.get("color_palette", []),
            visual_stats=data.get("visual_stats", {}),
        )


class SemanticContext:
    """
    Semantic metadata for MCP/RAG integration and LLM interpretation.

    Provides structured information about the data's meaning, context,
    and relationships for improved discoverability and understanding.
    """

    def __init__(
        self,
        natural_description: str = "",
        semantic_tags: Optional[List[str]] = None,
        geographic_context: Optional[Dict[str, Any]] = None,
        temporal_context: Optional[Dict[str, Any]] = None,
        data_insights: Optional[Dict[str, Any]] = None,
        relationships: Optional[List[Dict[str, Any]]] = None,
        search_keywords: Optional[List[str]] = None,
    ):
        """
        Initialize semantic context.

        Args:
            natural_description: Human-readable description for LLMs
            semantic_tags: Categorical tags for classification
            geographic_context: Place names, administrative regions, etc.
            temporal_context: Time period characteristics, seasonality
            data_insights: Auto-generated statistical insights
            relationships: Links to related data packages
            search_keywords: Keywords for search and retrieval
        """
        self.natural_description = natural_description
        self.semantic_tags = semantic_tags or []
        self.geographic_context = geographic_context or {}
        self.temporal_context = temporal_context or {}
        self.data_insights = data_insights or {}
        self.relationships = relationships or []
        self.search_keywords = search_keywords or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "natural_description": self.natural_description,
            "semantic_tags": self.semantic_tags,
            "geographic_context": self.geographic_context,
            "temporal_context": self.temporal_context,
            "data_insights": self.data_insights,
            "relationships": self.relationships,
            "search_keywords": self.search_keywords,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SemanticContext":
        """Create from dictionary."""
        return cls(
            natural_description=data.get("natural_description", ""),
            semantic_tags=data.get("semantic_tags", []),
            geographic_context=data.get("geographic_context", {}),
            temporal_context=data.get("temporal_context", {}),
            data_insights=data.get("data_insights", {}),
            relationships=data.get("relationships", []),
            search_keywords=data.get("search_keywords", []),
        )


class MultiResolutionData:
    """
    Multi-resolution data support for different processing needs.

    Provides data at different levels of detail to support various
    use cases from quick overview to detailed analysis.
    """

    def __init__(
        self,
        overview: Optional[Dict[str, Any]] = None,
        summary_stats: Optional[Dict[str, Any]] = None,
        reduced_resolution: Optional[Dict[str, Any]] = None,
        full_resolution: Optional[Dict[str, Any]] = None,
        processed_variants: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        """
        Initialize multi-resolution data.

        Args:
            overview: High-level statistical overview
            summary_stats: Statistical summaries and distributions
            reduced_resolution: Downsampled version for quick processing
            full_resolution: Full detail data
            processed_variants: Alternative processed versions
        """
        self.overview = overview or {}
        self.summary_stats = summary_stats or {}
        self.reduced_resolution = reduced_resolution or {}
        self.full_resolution = full_resolution or {}
        self.processed_variants = processed_variants or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "overview": self.overview,
            "summary_stats": self.summary_stats,
            "reduced_resolution": self.reduced_resolution,
            "full_resolution": self.full_resolution,
            "processed_variants": self.processed_variants,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MultiResolutionData":
        """Create from dictionary."""
        return cls(
            overview=data.get("overview", {}),
            summary_stats=data.get("summary_stats", {}),
            reduced_resolution=data.get("reduced_resolution", {}),
            full_resolution=data.get("full_resolution", {}),
            processed_variants=data.get("processed_variants", {}),
        )


class Geometry:
    """
    Represents geometric data for spatial information.

    A flexible container for various geometric representations used in
    geospatial visualizations. Supports different geometry types and
    their associated coordinate data.

    Args:
        type: The geometry type (e.g., 'Point', 'LineString', 'Polygon',
          'MultiPolygon')
        value: The geometric data, format depends on type

    Example:
        >>> # Point geometry
        >>> point = Geometry("Point", {"coordinates": [-74.0059, 40.7128]})
        >>>
        >>> # Polygon geometry
        >>> polygon = Geometry("Polygon", {
        ...     "coordinates": [
        ...         [[-74.0, 40.7], [-74.0, 40.8], [-73.9, 40.8],
        ...          [-73.9, 40.7], [-74.0, 40.7]]
        ...     ]
        ... })
    """

    def __init__(self, type: str, value: Union[dict, List[dict]]):
        """
        Initialize a Geometry instance.

        Args:
            type: Geometry type string (Point, LineString, Polygon, etc.)
            value: Geometry data structure, typically GeoJSON-compatible
        """
        self.type = type
        self.value = value

    @classmethod
    def from_dict(cls, data: dict) -> "Geometry":
        """
        Create a Geometry instance from a dictionary.

        Args:
            data: Dictionary with 'type' and 'value' keys

        Returns:
            Geometry instance

        Raises:
            KeyError: If required keys are missing
        """
        return cls(type=data["type"], value=data["value"])

    def to_dict(self) -> dict:
        """
        Convert geometry to a JSON-serializable dictionary.

        Returns:
            Dictionary representation of geometry
        """
        return {"type": self.type, "value": self.value}


class Time:
    """
    Represents temporal information in ISO 8601 format.

    Provides flexible time representation supporting single timestamps,
    time spans, and time series. All times must be in ISO 8601 format
    and are validated upon creation.

    Supported time types:
    - **Timestamp**: Single point in time
    - **Span**: Time range with start and end
    - **Series**: Ordered list of timestamps

    Args:
        type: Time type - one of "Timestamp", "Span", or "Series"
        value: Time data - format depends on type

    Examples:
        >>> # Single timestamp
        >>> t1 = Time("Timestamp", "2023-01-01T12:00:00Z")
        >>>
        >>> # Time span
        >>> t2 = Time("Span", {"start": "2023-01-01T00:00:00Z", "end": "2023-01-02T00:00:00Z"})
        >>>
        >>> # Time series
        >>> t3 = Time("Series", ["2023-01-01T00:00:00Z", "2023-01-01T01:00:00Z"])
        >>>
        >>> # Using convenience methods
        >>> timestamp = Time.timestamp("2023-01-01T12:00:00Z")
        >>> span = Time.span("2023-01-01T00:00:00Z", "2023-01-02T00:00:00Z")
        >>> series = Time.series(["2023-01-01T00:00:00Z", "2023-01-01T01:00:00Z"])
    """

    def __init__(
        self,
        type: Literal["Timestamp", "Span", "Series"],
        value: Union[str, dict, List[str]],
    ):
        """
        Initialize a Time instance with validation.

        Args:
            type: Time type - "Timestamp", "Span", or "Series"
            value: Time data in appropriate format for the type

        Raises:
            ValueError: If type is invalid or value doesn't match type requirements
        """
        self.type = type
        self.value = value
        self._validate()

    def _validate(self) -> None:
        """
        Validate the time definition.

        Raises:
            ValueError: If time type or value format is invalid
        """
        if self.type not in TIME_TYPES:
            raise ValueError(
                f"Invalid time type: {self.type}. Must be one of {TIME_TYPES}"
            )

        if self.type == "Timestamp":
            if not isinstance(self.value, str):
                raise ValueError("Timestamp value must be a string")
            isodate.parse_datetime(self.value)  # Raises ValueError if invalid

        elif self.type == "Span":
            if (
                not isinstance(self.value, dict)
                or "start" not in self.value
                or "end" not in self.value
            ):
                raise ValueError("Span value must be a dict with 'start' and 'end'")
            start = isodate.parse_datetime(self.value["start"])
            end = isodate.parse_datetime(self.value["end"])
            if start >= end:
                raise ValueError("Span start must be before end")

        elif self.type == "Series":
            if not isinstance(self.value, list):
                raise ValueError("Series value must be a list")
            times = [isodate.parse_datetime(t) for t in self.value]
            if not times:
                raise ValueError("Series cannot be empty")
            if times != sorted(times):
                raise ValueError("Series timestamps must be sorted")

    def to_dict(self) -> dict:
        """
        Convert to a JSON-serializable dictionary.

        Returns:
            Dictionary with 'type' and 'value' keys
        """
        return {"type": self.type, "value": self.value}

    @classmethod
    def from_dict(cls, data: dict) -> "Time":
        """
        Create Time instance from a dictionary.

        Args:
            data: Dictionary with 'type' and 'value' keys

        Returns:
            Time instance

        Raises:
            KeyError: If required keys are missing
            ValueError: If time data is invalid
        """
        return cls(type=data["type"], value=data["value"])

    @classmethod
    def timestamp(cls, timestamp: str) -> "Time":
        """
        Create a Timestamp instance.

        Args:
            timestamp: ISO 8601 timestamp string

        Returns:
            Time instance of type Timestamp

        Example:
            >>> time_obj = Time.timestamp("2023-01-01T12:00:00Z")
        """
        return cls(type="Timestamp", value=timestamp)

    @classmethod
    def span(cls, start: str, end: str) -> "Time":
        """
        Create a Span instance.

        Args:
            start: ISO 8601 start timestamp
            end: ISO 8601 end timestamp

        Returns:
            Time instance of type Span

        Example:
            >>> time_obj = Time.span("2023-01-01T00:00:00Z", "2023-01-02T00:00:00Z")
        """
        return cls(type="Span", value={"start": start, "end": end})

    @classmethod
    def series(cls, timestamps: List[str]) -> "Time":
        """
        Create a Series instance.

        Args:
            timestamps: List of ISO 8601 timestamp strings (must be sorted)

        Returns:
            Time instance of type Series

        Example:
            >>> time_obj = Time.series([
            ...     "2023-01-01T00:00:00Z",
            ...     "2023-01-01T01:00:00Z",
            ...     "2023-01-01T02:00:00Z"
            ... ])
        """
        return cls(type="Series", value=timestamps)


class MyrezeDataPackage:
    """
    Enhanced container for geospatial data with multimodal LLM support.

    An advanced MyrezeDataPackage that encapsulates geospatial data with
    comprehensive metadata, visual representations, and semantic context
    optimized for LLM-based agents and multimodal AI systems.

    Enhanced features:
    - **Visual Summaries**: Thumbnails and previews for multimodal LLMs
    - **Semantic Context**: Natural language descriptions and tagging
    - **Multi-Resolution Data**: Different detail levels for various uses
    - **MCP/RAG Integration**: Structured metadata for search and retrieval
    - **Platform-Agnostic Export**: Multiple serialization formats
    - **Multi-Agent Context**: Cumulative context from multiple agents

    Args:
        id: Unique identifier for the data package
        data: Core geospatial data dictionary
        time: Temporal information (Time instance)
        unreal_visualization: Optional Unreal Engine renderer
        threejs_visualization: Optional Three.js renderer
        metadata: Optional additional metadata dictionary
        version: Package format version (default: "1.0.0")
        visualization_type: Semantic type hint for data interpretation
        validate_on_init: Whether to validate package on creation
        visual_summary: Visual representations for multimodal LLMs
        semantic_context: Semantic metadata for MCP/RAG integration
        multi_resolution_data: Multi-resolution data support
        agent_context: Multi-agent context with attribution and audit trails

    Example:
        >>> import numpy as np
        >>> from myreze.data import MyrezeDataPackage, Time, SemanticContext
        >>> from myreze.data.agent_context import add_expert_opinion
        >>>
        >>> # Create enhanced data package
        >>> data = {
        ...     "grid": np.random.rand(100, 100) * 30 + 10,
        ...     "bounds": [-74.0, 40.7, -73.9, 40.8],
        ...     "units": "celsius"
        ... }
        >>>
        >>> semantic_context = SemanticContext(
        ...     natural_description="Temperature map showing heat distribution across NYC",
        ...     semantic_tags=["weather", "urban", "temperature"],
        ...     geographic_context={"city": "New York", "region": "Northeast US"}
        ... )
        >>>
        >>> package = MyrezeDataPackage(
        ...     id="nyc-temperature-enhanced",
        ...     data=data,
        ...     time=Time.timestamp("2023-06-15T14:30:00Z"),
        ...     visualization_type="heatmap",
        ...     semantic_context=semantic_context
        ... )
        >>>
        >>> # Add expert context as package moves through agents
        >>> add_expert_opinion(
        ...     package,
        ...     "This shows a strong urban heat island effect typical for summer afternoons",
        ...     expert_id="weather_forecasting_agent",
        ...     confidence=0.9
        ... )
    """

    def __init__(
        self,
        id: str,
        data: Dict[str, Any],
        time: Time,
        unreal_visualization: Optional[UnrealRenderer] = None,
        threejs_visualization: Optional[ThreeJSRenderer] = None,
        metadata: Optional[Dict[str, Any]] = None,
        version: str = "1.0.0",
        visualization_type: str = "",
        validate_on_init: bool = False,
        # Enhanced LLM/multimodal features
        visual_summary: Optional[VisualSummary] = None,
        semantic_context: Optional[SemanticContext] = None,
        multi_resolution_data: Optional[MultiResolutionData] = None,
        agent_context: Optional["MultiAgentContext"] = None,
    ):
        """
        Initialize an enhanced MyrezeDataPackage.

        Args:
            id: Unique identifier for this data package
            data: Dictionary containing the geospatial data
            time: Time instance specifying temporal information
            unreal_visualization: Optional UnrealRenderer instance
            threejs_visualization: Optional ThreeJSRenderer instance
            metadata: Optional dictionary with additional information
            version: Package format version string
            visualization_type: Semantic hint for data interpretation
            validate_on_init: If True, validates package structure on creation
            visual_summary: Visual representations for multimodal LLMs
            semantic_context: Semantic metadata for MCP/RAG integration
            multi_resolution_data: Multi-resolution data support
            agent_context: Multi-agent context with attribution
        """
        # Core fields (backwards compatible)
        self.id = id
        self.data = data
        self.time = time

        # Validate renderer instances
        if unreal_visualization is not None and not isinstance(
            unreal_visualization, UnrealRenderer
        ):
            raise TypeError(
                "unreal_visualization must be an instance of UnrealRenderer"
            )
        self.unreal_visualization = unreal_visualization

        if threejs_visualization is not None and not isinstance(
            threejs_visualization, ThreeJSRenderer
        ):
            raise TypeError(
                "threejs_visualization must be an instance of ThreeJSRenderer"
            )
        self.threejs_visualization = threejs_visualization

        self.metadata = metadata or {}
        self.version = version
        self.visualization_type = visualization_type

        # Enhanced LLM/multimodal features
        self.visual_summary = visual_summary
        self.semantic_context = semantic_context
        self.multi_resolution_data = multi_resolution_data
        self.agent_context = agent_context

        # Auto-generate missing components if possible
        if not self.semantic_context and self.visualization_type:
            self.semantic_context = self._generate_basic_semantic_context()

        # Validation
        if validate_on_init:
            self._validate()

    def _generate_basic_semantic_context(self) -> SemanticContext:
        """Auto-generate basic semantic context from available data."""
        # Extract basic insights from data structure
        data_insights = self._analyze_data_structure()

        # Generate natural description
        description = self._generate_natural_description()

        # Extract geographic context from bounds if available
        geo_context = self._extract_geographic_context()

        # Generate semantic tags based on visualization type and metadata
        tags = self._generate_semantic_tags()

        return SemanticContext(
            natural_description=description,
            semantic_tags=tags,
            geographic_context=geo_context,
            data_insights=data_insights,
            search_keywords=tags + [self.visualization_type, self.id],
        )

    def _analyze_data_structure(self) -> Dict[str, Any]:
        """Analyze data structure and extract insights."""
        insights = {
            "data_fields": list(self.data.keys()),
            "visualization_type": self.visualization_type,
            "timestamp": datetime.now().isoformat(),
        }

        # Analyze grid data if present
        if "grid" in self.data:
            grid = self.data["grid"]
            if isinstance(grid, (list, np.ndarray)):
                grid_array = np.array(grid)
                insights["grid_shape"] = list(grid_array.shape)
                if grid_array.size > 0:
                    insights["value_range"] = [
                        float(np.min(grid_array)),
                        float(np.max(grid_array)),
                    ]
                    insights["mean_value"] = float(np.mean(grid_array))

        # Analyze point data if present
        if "locations" in self.data and "values" in self.data:
            insights["num_points"] = len(self.data["locations"])
            if self.data["values"]:
                values = np.array(self.data["values"])
                insights["value_range"] = [float(np.min(values)), float(np.max(values))]
                insights["mean_value"] = float(np.mean(values))

        return insights

    def _generate_natural_description(self) -> str:
        """Generate natural language description of the data."""
        viz_type = self.visualization_type or "geospatial data"

        # Base description from visualization type
        type_descriptions = {
            "heatmap": "a heat map showing spatial distribution of values",
            "flat_overlay": "a map overlay displaying spatial data",
            "point_cloud": "discrete data points at specific locations",
            "vector_field": "directional data showing flow or movement patterns",
            "trajectory": "time-based path or movement data",
            "terrain": "elevation or topographic data",
        }

        base_desc = type_descriptions.get(viz_type, f"{viz_type} visualization")

        # Add temporal context
        time_desc = ""
        if self.time.type == "Timestamp":
            time_desc = f" at {self.time.value}"
        elif self.time.type == "Span":
            time_desc = f" from {self.time.value['start']} to {self.time.value['end']}"
        elif self.time.type == "Series":
            time_desc = f" across {len(self.time.value)} time points"

        # Add geographic context if bounds available
        geo_desc = ""
        if "bounds" in self.data:
            bounds = self.data["bounds"]
            if len(bounds) == 4:
                geo_desc = f" covering area from {bounds[0]:.2f}, {bounds[1]:.2f} to {bounds[2]:.2f}, {bounds[3]:.2f}"

        # Add units if available
        units_desc = ""
        if "units" in self.data:
            units_desc = f" measured in {self.data['units']}"

        return f"This package contains {base_desc}{time_desc}{geo_desc}{units_desc}."

    def _extract_geographic_context(self) -> Dict[str, Any]:
        """Extract geographic context from data."""
        context = {}

        if "bounds" in self.data:
            bounds = self.data["bounds"]
            if len(bounds) == 4:
                west, south, east, north = bounds
                context["bounding_box"] = {
                    "west": west,
                    "south": south,
                    "east": east,
                    "north": north,
                }

                # Rough geographic classification
                center_lat = (south + north) / 2
                center_lon = (west + east) / 2
                context["center_point"] = {"lat": center_lat, "lon": center_lon}

                # Basic geographic classification
                if -130 <= center_lon <= -60 and 20 <= center_lat <= 50:
                    context["region"] = "North America"
                elif -15 <= center_lon <= 45 and 35 <= center_lat <= 70:
                    context["region"] = "Europe"
                elif 95 <= center_lon <= 145 and 20 <= center_lat <= 45:
                    context["region"] = "East Asia"

        return context

    def _generate_semantic_tags(self) -> List[str]:
        """Generate semantic tags based on data characteristics."""
        tags = []

        # Add visualization type
        if self.visualization_type:
            tags.append(self.visualization_type)

        # Add tags based on data fields and metadata
        if (
            "temperature" in str(self.data).lower()
            or "temp" in str(self.metadata).lower()
        ):
            tags.extend(["weather", "temperature", "atmospheric"])

        if "wind" in str(self.data).lower() or "wind" in str(self.metadata).lower():
            tags.extend(["weather", "wind", "atmospheric"])

        if (
            "precipitation" in str(self.data).lower()
            or "rain" in str(self.metadata).lower()
        ):
            tags.extend(["weather", "precipitation", "atmospheric"])

        if (
            "elevation" in str(self.data).lower()
            or "terrain" in str(self.metadata).lower()
        ):
            tags.extend(["terrain", "topography", "geological"])

        # Add temporal tags
        if self.time.type == "Series":
            tags.append("time_series")

        # Remove duplicates
        return list(set(tags))

    def _validate(self) -> None:
        """
        Validate the data package against the MDP schema.

        Raises:
            ValueError: If validation fails
        """
        validate_mdp(self.to_dict())

    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get schema information for this package's visualization type.

        Returns:
            Dictionary with schema requirements and format information
        """
        return VISUALIZATION_SCHEMAS.get(
            self.visualization_type,
            {
                "description": f"Custom visualization type: {self.visualization_type}",
                "required_fields": "Unknown - custom type",
                "optional_fields": "Unknown - custom type",
            },
        )

    @staticmethod
    def get_available_visualization_types() -> List[str]:
        """Get list of all supported visualization types."""
        return VISUALIZATION_TYPES.copy()

    @staticmethod
    def get_visualization_schema(viz_type: str) -> Dict[str, Any]:
        """Get schema information for a specific visualization type."""
        return VISUALIZATION_SCHEMAS.get(viz_type, {})

    def generate_visual_summary(
        self, auto_generate: bool = True
    ) -> Optional[VisualSummary]:
        """
        Generate visual summary for multimodal LLM consumption.

        Args:
            auto_generate: Whether to auto-generate if renderers available

        Returns:
            VisualSummary instance or None if generation fails
        """
        if not auto_generate:
            return self.visual_summary

        try:
            # Try to generate thumbnail using available renderers
            thumbnail_png = None
            visual_stats = {}

            # Generate visual hash from data
            data_str = json.dumps(self.data, default=str, sort_keys=True)
            visual_hash = hashlib.md5(data_str.encode()).hexdigest()

            # Extract color information from data if possible
            color_palette = self._extract_color_palette()

            # Basic visual statistics
            visual_stats = {
                "data_complexity": len(str(self.data)),
                "field_count": len(self.data),
                "has_grid_data": "grid" in self.data,
                "has_point_data": "locations" in self.data,
            }

            return VisualSummary(
                thumbnail_png=thumbnail_png,
                visual_hash=visual_hash,
                color_palette=color_palette,
                visual_stats=visual_stats,
            )

        except Exception as e:
            warnings.warn(f"Failed to generate visual summary: {e}")
            return None

    def _extract_color_palette(self) -> List[str]:
        """Extract representative color palette from metadata."""
        colors = []

        # Check metadata for color information
        if "colormap" in self.metadata:
            colormap = self.metadata["colormap"]
            # Map common colormaps to representative colors
            colormap_colors = {
                "viridis": ["#440154", "#31688e", "#35b779", "#fde725"],
                "plasma": ["#0d0887", "#7e03a8", "#cc4778", "#f89441", "#f0f921"],
                "coolwarm": ["#3b4cc0", "#6788ee", "#b40426", "#dc143c"],
                "blues": ["#f7fbff", "#c6dbef", "#4292c6", "#08519c"],
            }
            colors = colormap_colors.get(colormap, [])

        # Default colors based on visualization type
        if not colors:
            type_colors = {
                "heatmap": ["#ff0000", "#ffff00", "#0000ff"],
                "point_cloud": ["#1f77b4", "#ff7f0e", "#2ca02c"],
                "vector_field": ["#8b0000", "#ff4500", "#1e90ff"],
                "flat_overlay": ["#2e8b57", "#daa520", "#cd853f"],
            }
            colors = type_colors.get(self.visualization_type, ["#1f77b4"])

        return colors

    def to_dict(self, include_enhanced_features: bool = True) -> Dict[str, Any]:
        """
        Convert the data package to a JSON-serializable dictionary.

        Args:
            include_enhanced_features: Whether to include new LLM features

        Returns:
            Dictionary representation suitable for JSON serialization
        """
        # Convert NumPy arrays and bytes for JSON compatibility
        data = self.data.copy()
        for key, value in data.items():
            if isinstance(value, np.ndarray):
                data[key] = value.tolist()
            elif isinstance(value, bytes):
                data[key] = base64.b64encode(value).decode("utf-8")
            elif isinstance(value, list):
                converted_list = []
                for item in value:
                    if isinstance(item, bytes):
                        converted_list.append(base64.b64encode(item).decode("utf-8"))
                    else:
                        converted_list.append(item)
                data[key] = converted_list

        # Base package structure (backwards compatible)
        package_dict = {
            "version": self.version,
            "type": "MyrezeDataPackage",
            "id": self.id,
            "data": data,
            "time": self.time.to_dict(),
            "unreal_visualization": (
                self.unreal_visualization.to_dict()
                if self.unreal_visualization
                else None
            ),
            "threejs_visualization": (
                self.threejs_visualization.to_dict()
                if self.threejs_visualization
                else None
            ),
            "metadata": self.metadata,
            "visualization_type": self.visualization_type,
        }

        # Add enhanced features if requested
        if include_enhanced_features:
            package_dict.update(
                {
                    "visual_summary": (
                        self.visual_summary.to_dict() if self.visual_summary else None
                    ),
                    "semantic_context": (
                        self.semantic_context.to_dict()
                        if self.semantic_context
                        else None
                    ),
                    "multi_resolution_data": (
                        self.multi_resolution_data.to_dict()
                        if self.multi_resolution_data
                        else None
                    ),
                    "agent_context": (
                        self.agent_context.to_dict() if self.agent_context else None
                    ),
                }
            )

        return package_dict

    def to_json(self, include_enhanced_features: bool = True) -> str:
        """
        Convert the data package to a JSON string.

        Args:
            include_enhanced_features: Whether to include new LLM features

        Returns:
            JSON string representation of the package
        """
        return json.dumps(self.to_dict(include_enhanced_features))

    def to_threejs(self, params: Optional[Dict[str, Any]] = None) -> Any:
        """Generate Three.js visualization output."""
        if not self.threejs_visualization:
            raise ValueError("No Three.js renderer configured for this package")
        return self.threejs_visualization.render(self.data, params or {})

    def to_unreal(self, params: Optional[Dict[str, Any]] = None) -> Any:
        """Generate Unreal Engine visualization output."""
        if not self.unreal_visualization:
            raise ValueError("No Unreal renderer configured for this package")
        return self.unreal_visualization.render(self.data, params or {})

    def get_llm_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary optimized for LLM consumption.

        Returns:
            Dictionary with all information LLMs need to understand the package
        """
        summary = {
            "package_id": self.id,
            "visualization_type": self.visualization_type,
            "time_info": {"type": self.time.type, "value": self.time.value},
            "data_structure": {
                "fields": list(self.data.keys()),
                "field_types": {k: type(v).__name__ for k, v in self.data.items()},
            },
        }

        # Add semantic context if available
        if self.semantic_context:
            summary["semantic_context"] = self.semantic_context.to_dict()

        # Add visual information if available
        if self.visual_summary:
            summary["visual_info"] = {
                "has_thumbnail": self.visual_summary.thumbnail_png is not None,
                "color_palette": self.visual_summary.color_palette,
                "visual_stats": self.visual_summary.visual_stats,
            }

        # Add agent context summary
        if self.agent_context:
            summary["agent_context"] = self.agent_context.get_context_summary()
            summary["context_narrative"] = (
                self.agent_context.generate_narrative_summary()
            )

        # Add metadata
        summary["metadata"] = self.metadata

        return summary

    @classmethod
    def from_json(cls, json_str: str) -> "MyrezeDataPackage":
        """Create a data package from a JSON string."""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MyrezeDataPackage":
        """
        Create a data package from a dictionary.

        Supports both legacy and enhanced formats for backwards compatibility.
        """
        # Handle renderers
        threejs_visualization = (
            ThreeJSRenderer.from_dict(data["threejs_visualization"])
            if data.get("threejs_visualization")
            else None
        )
        unreal_visualization = (
            UnrealRenderer.from_dict(data["unreal_visualization"])
            if data.get("unreal_visualization")
            else None
        )

        # Handle enhanced features (new)
        visual_summary = None
        if data.get("visual_summary"):
            visual_summary = VisualSummary.from_dict(data["visual_summary"])

        semantic_context = None
        if data.get("semantic_context"):
            semantic_context = SemanticContext.from_dict(data["semantic_context"])

        multi_resolution_data = None
        if data.get("multi_resolution_data"):
            multi_resolution_data = MultiResolutionData.from_dict(
                data["multi_resolution_data"]
            )

        # Handle agent context (new)
        agent_context = None
        if data.get("agent_context"):
            # Import here to avoid circular imports
            from myreze.data.agent_context import MultiAgentContext

            agent_context = MultiAgentContext.from_dict(data["agent_context"])

        return cls(
            id=data["id"],
            data=data["data"],
            time=Time.from_dict(data["time"]),
            threejs_visualization=threejs_visualization,
            unreal_visualization=unreal_visualization,
            metadata=data.get("metadata", {}),
            version=data.get("version", "1.0.0"),
            visualization_type=data.get("visualization_type", ""),
            visual_summary=visual_summary,
            semantic_context=semantic_context,
            multi_resolution_data=multi_resolution_data,
            agent_context=agent_context,
            validate_on_init=True,
        )

    def add_agent_context(
        self,
        content: str,
        agent_id: str,
        context_type: str = "analysis",
        agent_type: str = "llm_agent",
        annotation_type: str = "analysis",
        confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "AgentAnnotation":
        """
        Add context from an agent to this package.

        Args:
            content: The context content (e.g., expert opinion, analysis result)
            agent_id: Unique identifier for the agent adding context
            context_type: Type of context ("expert_opinion", "analysis", "validation", etc.)
            agent_type: Type of agent ("llm_agent", "expert_system", "human_expert")
            annotation_type: Specific type of annotation
            confidence: Confidence score (0.0-1.0)
            metadata: Additional metadata about the context

        Returns:
            The created AgentAnnotation

        Example:
            >>> # Weather expert adds opinion
            >>> package.add_agent_context(
            ...     "This wind pattern indicates record-breaking intensity for this region",
            ...     agent_id="weather_expert_v2",
            ...     context_type="expert_opinion",
            ...     confidence=0.95
            ... )
            >>>
            >>> # Analysis agent adds statistical insight
            >>> package.add_agent_context(
            ...     "Temperature variance is 2.3 standard deviations above normal",
            ...     agent_id="statistical_analysis_agent",
            ...     context_type="analysis",
            ...     annotation_type="statistical"
            ... )
        """
        # Import here to avoid circular imports
        global MultiAgentContext
        if MultiAgentContext is None:
            from myreze.data.agent_context import MultiAgentContext

        # Initialize agent context if not present
        if self.agent_context is None:
            self.agent_context = MultiAgentContext(package_id=self.id)

        return self.agent_context.add_context(
            content=content,
            agent_id=agent_id,
            context_type=context_type,
            agent_type=agent_type,
            annotation_type=annotation_type,
            confidence=confidence,
            metadata=metadata,
        )

    def get_agent_context_summary(self) -> Dict[str, Any]:
        """
        Get summary of all agent context added to this package.

        Returns:
            Dictionary with comprehensive summary of agent contributions

        Example:
            >>> summary = package.get_agent_context_summary()
            >>> print(f"Total agents contributed: {summary['unique_agents']}")
            >>> print(f"Expert opinions: {len(summary.get('expert_opinions', []))}")
        """
        if not self.agent_context:
            return {"message": "No agent context available"}

        return self.agent_context.get_context_summary()

    def get_context_narrative(self) -> str:
        """
        Get natural language summary of all agent context.

        Returns:
            Human-readable narrative of expert opinions and analysis

        Example:
            >>> narrative = package.get_context_narrative()
            >>> print(narrative)
            # Output: "Expert opinions:
            #         • weather_expert: This shows strong urban heat island effect
            #         • climate_analyst: Temperature anomaly is significant
            #         Analysis: Statistical variance above normal range"
        """
        if not self.agent_context:
            return "No additional context has been added by agents."

        return self.agent_context.generate_narrative_summary()

    def get_expert_opinions(self) -> List["AgentAnnotation"]:
        """
        Get all expert opinions added to this package.

        Returns:
            List of expert opinion annotations
        """
        if not self.agent_context:
            return []

        return self.agent_context.get_expert_opinions()

    def map_tile(
        self,
        x: int,
        y: int,
        z: int,
        tile_size: int = 256,
        return_format: str = "bytes",
        style: Optional[Dict[str, Any]] = None,
    ) -> Union[bytes, str, "Image.Image"]:
        """
        Generate a map tile for the given XYZ coordinates.

        This method renders the data package as a 256x256 PNG tile compatible
        with web map tile services (XYZ/Slippy Map tiles) used by OpenStreetMap,
        Google Maps, Leaflet, Mapbox, etc.

        Args:
            x: Tile X coordinate
            y: Tile Y coordinate
            z: Zoom level (1-18, values outside this range are clamped)
            tile_size: Output tile size in pixels (default 256)
            return_format: Output format - "bytes", "base64", or "image"
            style: Optional styling parameters (colormap, vmin, vmax, etc.)

        Returns:
            PNG tile data in the requested format:
            - "bytes": PNG as bytes (default)
            - "base64": Base64-encoded PNG string
            - "image": PIL Image object

        Raises:
            ValueError: If required metadata is missing or data format is unsupported
            ImportError: If required dependencies are not available

        Example:
            >>> import numpy as np
            >>> from myreze.data import MyrezeDataPackage, Time
            >>>
            >>> # Create package with grid data
            >>> data = {
            ...     "grid": np.random.rand(100, 100) * 30 + 10,
            ...     "bounds": [-74.0, 40.7, -73.9, 40.8],  # NYC area
            ... }
            >>> metadata = {"crs": "EPSG:4326", "colormap": "viridis"}
            >>>
            >>> package = MyrezeDataPackage(
            ...     id="temperature-map",
            ...     data=data,
            ...     time=Time.timestamp("2023-06-15T14:30:00Z"),
            ...     metadata=metadata,
            ...     visualization_type="map_tile"
            ... )
            >>>
            >>> # Get tile covering Manhattan at zoom level 10
            >>> tile_bytes = package.map_tile(x=301, y=384, z=10)
            >>>
            >>> # Get as base64 for JavaScript
            >>> tile_b64 = package.map_tile(x=301, y=384, z=10, return_format="base64")
            >>>
            >>> # Get with custom styling
            >>> styled_tile = package.map_tile(
            ...     x=301, y=384, z=10,
            ...     style={"colormap": "plasma", "vmin": 15, "vmax": 25}
            ... )
            >>>
            >>> # Single-channel PNG example (elevation data)
            >>> elevation_data = {"png_bytes": base64_encoded_grayscale_png}
            >>> elevation_metadata = {"bounds": bounds, "crs": "EPSG:4326", "colormap": "terrain"}
            >>> elevation_pkg = MyrezeDataPackage(
            ...     id="elevation-map", data=elevation_data, time=time,
            ...     metadata=elevation_metadata, visualization_type="map_tile"
            ... )
            >>> elevation_tile = elevation_pkg.map_tile(x=301, y=384, z=10)  # Applies terrain colormap

        Note:
            - Tiles are generated on-demand with no precomputation
            - Returns transparent PNG if no data overlaps the requested tile
            - Supports both numeric grid data and PNG overlay data
            - Single-channel PNGs automatically apply colormaps for visualization
            - Uses Web Mercator projection (EPSG:3857) for tile coordinates
            - Source data can be in EPSG:4326 (WGS84) or EPSG:3857 (Web Mercator)
        """
        from myreze.viz.tiles.xyz import render_xyz_tile, encode_tile_png

        # Render the tile as RGBA array
        rgba_tile = render_xyz_tile(
            data=self.data,
            metadata=self.metadata or {},
            x=x,
            y=y,
            z=z,
            tile_size=tile_size,
            style=style,
        )

        # Encode in requested format
        return encode_tile_png(rgba_tile, return_format)
