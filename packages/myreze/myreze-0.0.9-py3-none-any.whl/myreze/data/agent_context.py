"""
Agent Context Management for MyrezeDataPackage

This module provides structured support for cumulative context from multiple
LLM agents, with proper attribution, audit trails, and expert analysis tracking.
Designed to support workflows where data packages are passed between different
agents that each add their own context and insights.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid


class AgentAnnotation:
    """
    Individual annotation or insight from a specific agent.

    Represents a single piece of context, analysis, or commentary
    added by an LLM agent or expert system, with full attribution
    and metadata tracking.
    """

    def __init__(
        self,
        content: str,
        agent_id: str,
        agent_type: str = "llm_agent",
        annotation_type: str = "analysis",
        confidence: Optional[float] = None,
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        references: Optional[List[str]] = None,
    ):
        """
        Initialize an agent annotation.

        Args:
            content: The actual annotation/analysis content
            agent_id: Unique identifier for the agent that created this
            agent_type: Type of agent (e.g., "llm_agent", "expert_system", "human_expert")
            annotation_type: Type of annotation (e.g., "analysis", "opinion", "correction", "enhancement")
            confidence: Confidence score for this annotation (0.0-1.0)
            timestamp: ISO 8601 timestamp when annotation was created
            metadata: Additional metadata about the annotation
            references: References to other annotations or external sources
        """
        self.id = str(uuid.uuid4())
        self.content = content
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.annotation_type = annotation_type
        self.confidence = confidence
        self.timestamp = timestamp or datetime.now().isoformat()
        self.metadata = metadata or {}
        self.references = references or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "annotation_type": self.annotation_type,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "references": self.references,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentAnnotation":
        """Create from dictionary."""
        annotation = cls(
            content=data["content"],
            agent_id=data["agent_id"],
            agent_type=data.get("agent_type", "llm_agent"),
            annotation_type=data.get("annotation_type", "analysis"),
            confidence=data.get("confidence"),
            timestamp=data.get("timestamp"),
            metadata=data.get("metadata", {}),
            references=data.get("references", []),
        )
        annotation.id = data.get("id", annotation.id)
        return annotation


class AgentContextChain:
    """
    Chain of context additions from multiple agents.

    Manages the accumulation of context, analysis, and expert opinions
    as a data package moves through different LLM agents and systems.
    Provides full audit trail and attribution tracking.
    """

    def __init__(
        self,
        annotations: Optional[List[AgentAnnotation]] = None,
        context_type: str = "general",
        chain_metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize an agent context chain.

        Args:
            annotations: List of existing annotations
            context_type: Type of context chain (e.g., "analysis", "expert_opinion", "validation")
            chain_metadata: Metadata about the entire chain
        """
        self.annotations = annotations or []
        self.context_type = context_type
        self.chain_metadata = chain_metadata or {}
        self.created_at = datetime.now().isoformat()
        self.last_modified = self.created_at

    def add_annotation(
        self,
        content: str,
        agent_id: str,
        agent_type: str = "llm_agent",
        annotation_type: str = "analysis",
        confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        references: Optional[List[str]] = None,
    ) -> AgentAnnotation:
        """
        Add a new annotation to the chain.

        Args:
            content: The annotation content
            agent_id: ID of the agent adding this annotation
            agent_type: Type of agent
            annotation_type: Type of annotation
            confidence: Confidence score
            metadata: Additional metadata
            references: References to other annotations or sources

        Returns:
            The created AgentAnnotation
        """
        annotation = AgentAnnotation(
            content=content,
            agent_id=agent_id,
            agent_type=agent_type,
            annotation_type=annotation_type,
            confidence=confidence,
            metadata=metadata,
            references=references,
        )

        self.annotations.append(annotation)
        self.last_modified = datetime.now().isoformat()

        return annotation

    def get_annotations_by_type(self, annotation_type: str) -> List[AgentAnnotation]:
        """Get all annotations of a specific type."""
        return [
            ann for ann in self.annotations if ann.annotation_type == annotation_type
        ]

    def get_annotations_by_agent(self, agent_id: str) -> List[AgentAnnotation]:
        """Get all annotations from a specific agent."""
        return [ann for ann in self.annotations if ann.agent_id == agent_id]

    def get_latest_annotation(self) -> Optional[AgentAnnotation]:
        """Get the most recently added annotation."""
        return self.annotations[-1] if self.annotations else None

    def get_consensus_view(self) -> Dict[str, Any]:
        """
        Generate a consensus view from all annotations.

        Returns:
            Dictionary with aggregated insights and consensus information
        """
        if not self.annotations:
            return {}

        # Group by annotation type
        by_type = {}
        for ann in self.annotations:
            if ann.annotation_type not in by_type:
                by_type[ann.annotation_type] = []
            by_type[ann.annotation_type].append(ann)

        # Calculate consensus metrics
        consensus = {
            "total_annotations": len(self.annotations),
            "unique_agents": len(set(ann.agent_id for ann in self.annotations)),
            "annotation_types": list(by_type.keys()),
            "by_type": {},
        }

        for ann_type, annotations in by_type.items():
            consensus["by_type"][ann_type] = {
                "count": len(annotations),
                "agents": [ann.agent_id for ann in annotations],
                "avg_confidence": (
                    sum(ann.confidence for ann in annotations if ann.confidence)
                    / len([ann for ann in annotations if ann.confidence])
                    if any(ann.confidence for ann in annotations)
                    else None
                ),
                "latest_content": annotations[-1].content,
            }

        return consensus

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "annotations": [ann.to_dict() for ann in self.annotations],
            "context_type": self.context_type,
            "chain_metadata": self.chain_metadata,
            "created_at": self.created_at,
            "last_modified": self.last_modified,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentContextChain":
        """Create from dictionary."""
        annotations = [
            AgentAnnotation.from_dict(ann_data)
            for ann_data in data.get("annotations", [])
        ]

        chain = cls(
            annotations=annotations,
            context_type=data.get("context_type", "general"),
            chain_metadata=data.get("chain_metadata", {}),
        )

        chain.created_at = data.get("created_at", chain.created_at)
        chain.last_modified = data.get("last_modified", chain.last_modified)

        return chain


class MultiAgentContext:
    """
    Complete multi-agent context management for a data package.

    Manages multiple context chains for different types of analysis
    and expert opinions, providing a comprehensive audit trail and
    attribution system for cumulative context from multiple agents.
    """

    def __init__(
        self,
        context_chains: Optional[Dict[str, AgentContextChain]] = None,
        package_id: Optional[str] = None,
    ):
        """
        Initialize multi-agent context.

        Args:
            context_chains: Dictionary mapping context types to chains
            package_id: ID of the associated data package
        """
        self.context_chains = context_chains or {}
        self.package_id = package_id
        self.created_at = datetime.now().isoformat()
        self.last_modified = self.created_at

    def add_context(
        self,
        content: str,
        agent_id: str,
        context_type: str = "analysis",
        agent_type: str = "llm_agent",
        annotation_type: str = "analysis",
        confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        references: Optional[List[str]] = None,
    ) -> AgentAnnotation:
        """
        Add context to the appropriate chain.

        Args:
            content: The context content
            agent_id: ID of the agent adding context
            context_type: Type of context chain to add to
            agent_type: Type of agent
            annotation_type: Type of annotation
            confidence: Confidence score
            metadata: Additional metadata
            references: References to other annotations or sources

        Returns:
            The created AgentAnnotation
        """
        # Create chain if it doesn't exist
        if context_type not in self.context_chains:
            self.context_chains[context_type] = AgentContextChain(
                context_type=context_type
            )

        annotation = self.context_chains[context_type].add_annotation(
            content=content,
            agent_id=agent_id,
            agent_type=agent_type,
            annotation_type=annotation_type,
            confidence=confidence,
            metadata=metadata,
            references=references,
        )

        self.last_modified = datetime.now().isoformat()
        return annotation

    def get_expert_opinions(self) -> List[AgentAnnotation]:
        """Get all expert opinions across all chains."""
        opinions = []
        for chain in self.context_chains.values():
            opinions.extend(chain.get_annotations_by_type("expert_opinion"))
        return opinions

    def get_context_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of all context.

        Returns:
            Dictionary with summary of all context chains and annotations
        """
        summary = {
            "package_id": self.package_id,
            "total_chains": len(self.context_chains),
            "total_annotations": sum(
                len(chain.annotations) for chain in self.context_chains.values()
            ),
            "unique_agents": len(
                set(
                    ann.agent_id
                    for chain in self.context_chains.values()
                    for ann in chain.annotations
                )
            ),
            "context_types": list(self.context_chains.keys()),
            "created_at": self.created_at,
            "last_modified": self.last_modified,
            "chains": {},
        }

        for context_type, chain in self.context_chains.items():
            summary["chains"][context_type] = chain.get_consensus_view()

        return summary

    def get_agent_contributions(self, agent_id: str) -> List[AgentAnnotation]:
        """Get all contributions from a specific agent."""
        contributions = []
        for chain in self.context_chains.values():
            contributions.extend(chain.get_annotations_by_agent(agent_id))
        return contributions

    def generate_narrative_summary(self) -> str:
        """
        Generate a natural language summary of all context.

        Returns:
            Human-readable summary of expert opinions and analysis
        """
        if not self.context_chains:
            return "No additional context has been added to this data package."

        parts = []

        # Add expert opinions
        expert_opinions = self.get_expert_opinions()
        if expert_opinions:
            parts.append("Expert opinions:")
            for opinion in expert_opinions[-3:]:  # Last 3 opinions
                parts.append(f"• {opinion.agent_id}: {opinion.content}")

        # Add analysis insights
        for context_type, chain in self.context_chains.items():
            if context_type != "expert_opinion" and chain.annotations:
                latest = chain.get_latest_annotation()
                if latest:
                    parts.append(f"{context_type.title()}: {latest.content}")

        return "\n".join(parts) if parts else "No significant context available."

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "context_chains": {
                context_type: chain.to_dict()
                for context_type, chain in self.context_chains.items()
            },
            "package_id": self.package_id,
            "created_at": self.created_at,
            "last_modified": self.last_modified,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MultiAgentContext":
        """Create from dictionary."""
        context_chains = {
            context_type: AgentContextChain.from_dict(chain_data)
            for context_type, chain_data in data.get("context_chains", {}).items()
        }

        context = cls(context_chains=context_chains, package_id=data.get("package_id"))

        context.created_at = data.get("created_at", context.created_at)
        context.last_modified = data.get("last_modified", context.last_modified)

        return context


# Convenience functions for common use cases
def add_expert_opinion(
    package: "MyrezeDataPackage", opinion: str, expert_id: str, confidence: float = None
) -> AgentAnnotation:
    """
    Add an expert opinion to a data package.

    Args:
        package: The MyrezeDataPackage to add context to
        opinion: The expert opinion text
        expert_id: ID of the expert providing the opinion
        confidence: Confidence score for the opinion

    Returns:
        The created AgentAnnotation
    """
    if not hasattr(package, "agent_context") or package.agent_context is None:
        package.agent_context = MultiAgentContext(package_id=package.id)

    return package.agent_context.add_context(
        content=opinion,
        agent_id=expert_id,
        context_type="expert_opinion",
        agent_type="expert_system",
        annotation_type="expert_opinion",
        confidence=confidence,
    )


def add_analysis_result(
    package: "MyrezeDataPackage",
    analysis: str,
    agent_id: str,
    analysis_type: str = "statistical",
) -> AgentAnnotation:
    """
    Add an analysis result to a data package.

    Args:
        package: The MyrezeDataPackage to add context to
        analysis: The analysis result text
        agent_id: ID of the agent performing the analysis
        analysis_type: Type of analysis performed

    Returns:
        The created AgentAnnotation
    """
    if not hasattr(package, "agent_context") or package.agent_context is None:
        package.agent_context = MultiAgentContext(package_id=package.id)

    return package.agent_context.add_context(
        content=analysis,
        agent_id=agent_id,
        context_type="analysis",
        annotation_type=analysis_type,
    )
