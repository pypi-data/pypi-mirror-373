"""Flow-specific document base class for persistent pipeline data.

@public

This module provides the FlowDocument abstract base class for documents
that need to persist across Prefect flow runs and between pipeline steps.
"""

from typing import Literal, final

from .document import Document


class FlowDocument(Document):
    """Abstract base class for documents that persist across flow runs.

    @public

    FlowDocument is used for data that needs to be saved between pipeline
    steps and across multiple flow executions. These documents are typically
    written to the file system using the simple_runner utilities.

    Key characteristics:
    - Persisted to file system between pipeline steps
    - Survives across multiple flow runs
    - Used for flow inputs and outputs
    - Saved in directories named after the document's canonical name

    Creating FlowDocuments:
        **Use the `create` classmethod** for most use cases. It handles automatic
        conversion of various content types. Only use __init__ when you have bytes.

        >>> from enum import StrEnum
        >>>
        >>> # Simple document with pass:
        >>> class MyDoc(FlowDocument):
        ...     pass
        >>>
        >>> # Document with restricted file names:
        >>> class ConfigDoc(FlowDocument):
        ...     class FILES(StrEnum):
        ...         CONFIG = "config.yaml"
        ...         SETTINGS = "settings.json"
        >>>
        >>> # RECOMMENDED - automatic conversion:
        >>> doc = MyDoc.create(name="data.json", content={"key": "value"})
        >>> doc = ConfigDoc.create(name="config.yaml", content={"host": "localhost"})

    Persistence:
        Documents are saved to: {output_dir}/{canonical_name}/{filename}
        For example: output/my_doc/data.json

    Note:
        - Cannot instantiate FlowDocument directly - must subclass
        - Used with FlowConfig to define flow input/output types
        - No additional abstract methods to implement

    See Also:
        TaskDocument: For temporary documents within task execution
        TemporaryDocument: For documents that are never persisted
    """

    def __init__(
        self,
        *,
        name: str,
        content: bytes,
        description: str | None = None,
    ) -> None:
        """Initialize a FlowDocument with raw bytes content.

        Important:
            **Most users should use the `create` classmethod instead of __init__.**
            The create method provides automatic content conversion for various types
            (str, dict, list, Pydantic models) while __init__ only accepts bytes.

        Prevents direct instantiation of the abstract FlowDocument class.
        FlowDocument must be subclassed for specific document types.

        Args:
            name: Document filename (required, keyword-only)
            content: Document content as raw bytes (required, keyword-only)
            description: Optional human-readable description (keyword-only)

        Raises:
            TypeError: If attempting to instantiate FlowDocument directly
                      instead of using a concrete subclass.

        Example:
            >>> from enum import StrEnum
            >>>
            >>> # Simple subclass:
            >>> class MyFlowDoc(FlowDocument):
            ...     pass
            >>>
            >>> # With FILES restriction:
            >>> class RestrictedDoc(FlowDocument):
            ...     class FILES(StrEnum):
            ...         DATA = "data.json"
            ...         METADATA = "metadata.yaml"
            >>>
            >>> # Direct constructor - only for bytes:
            >>> doc = MyFlowDoc(name="test.bin", content=b"raw data")
            >>>
            >>> # RECOMMENDED - use create for automatic conversion:
            >>> doc = RestrictedDoc.create(name="data.json", content={"key": "value"})
            >>> # This would raise DocumentNameError:
            >>> # doc = RestrictedDoc.create(name="other.json", content={})
        """
        if type(self) is FlowDocument:
            raise TypeError("Cannot instantiate abstract FlowDocument class directly")
        super().__init__(name=name, content=content, description=description)

    @final
    def get_base_type(self) -> Literal["flow"]:
        """Return the base type identifier for flow documents.

        This method is final and cannot be overridden by subclasses.
        It identifies this document as a flow-persistent document.

        Returns:
            "flow" - Indicates this document persists across flow runs.

        Note:
            This determines the document's lifecycle and persistence behavior
            in the pipeline system.
        """
        return "flow"
