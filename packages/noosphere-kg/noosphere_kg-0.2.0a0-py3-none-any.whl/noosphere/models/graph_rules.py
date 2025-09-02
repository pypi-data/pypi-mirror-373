from typing import Optional
import yaml
from pydantic import BaseModel, field_serializer, model_validator


class GraphRules(BaseModel):
    """
    GraphRules is a Pydantic model that defines the rules for the graph.
    """

    strict_mode: Optional[bool] = True
    """
    Strict mode is a boolean flag that determines if the graph should be built
    in strict mode.
    """

    allowed_nodes: Optional[list[str]] = []
    """
    Allowed nodes is a list of nodes that are allowed to be in the graph.

    Example:

    ```yaml
    [
        "Microorganism",
        "Compound",
        "Enzyme",
        "Gene",
    ]
    ```
    """

    allowed_relationships: Optional[list[tuple[str, str, str]]] = []
    """
    Allowed relationships is a list of relationships that are allowed to be in
    the graph.

    Example:

    ```yaml
    [
        ("Microorganism", "CONTAINED_IN", "Location"),
        ("Microorganism", "PRODUCES", "Compound"),
        ("Microorganism", "PRODUCES", "Enzyme"),
        ("Microorganism", "PRODUCES", "Gene"),
    ]
    ```
    """

    node_properties: Optional[list[str]] = []
    """
    Node properties is a list of properties that are allowed to be in the graph.

    Example:

    ```yaml
    [
        "scientific_name",
        "strain_name",
        "organism_name",
        "compound_name",
        "enzyme_name",
        "gene_name",
        "protein_name",
        "metabolite_name",
        "crop_name",
    ]
    ```
    """

    relationship_properties: Optional[list[str]] = []
    """
    Relationship properties is a list of properties that are allowed to be in
    the graph.

    Example:

    ```yaml
    [
        "production_date",
        "crop_name",
    ]
    ```
    """

    base_entity_label: Optional[bool] = False
    """
    Base entity label is a boolean flag that determines if the graph should be
    built with base entity label.
    """

    prompt: Optional[str] = None
    """
    The prompt to pass to the LLM with additional instructions.
    """

    additional_instructions: Optional[str] = None
    """
    Allows you to add additional instructions to the prompt without having to
    change the whole prompt.
    """

    chunk_size: Optional[int] = 4000
    """
    Maximum size of chunks to return.
    """

    chunk_overlap: Optional[int] = 200
    """
    Overlap in characters between chunks.
    """

    add_start_index: Optional[bool] = False
    """
    If `True`, includes chunk's start index in metadata.
    """

    strip_whitespace: Optional[bool] = True
    """
    If `True`, strips whitespace from the start and end of every document.
    """

    # Create a validation for: `allowed_relationships` must be list of strings
    # or a list of 3-item tuples. For tuples, the first and last elements must
    # be in the `allowed_nodes` list.
    @model_validator(mode="before")
    def validate_allowed_relationships(cls, v):
        if (allowed_nodes := v.get("allowed_nodes", [])) is None:
            return v

        if (allowed_relationships := v.get("allowed_relationships", [])) is None:
            return v

        for rel in allowed_relationships:
            if isinstance(rel, str):
                continue

            if len(rel) != 3:
                raise ValueError(
                    "Each relationship must be either a string or a 3-item tuple"
                )

            start_node, _, end_node = rel

            if start_node not in allowed_nodes:
                raise ValueError(
                    f"Start node '{start_node}' is not in allowed_nodes list"
                )

            if end_node not in allowed_nodes:
                raise ValueError(f"End node '{end_node}' is not in allowed_nodes list")

        return v

    @classmethod
    def load_from_yaml_file(cls, file_path: str) -> "GraphRules":
        """
        Load configuration from a YAML file and return an instance of
        GraphRules.
        """

        with open(file_path, "r") as file:
            yaml_data = yaml.safe_load(file)

        return GraphRules(**yaml_data)

    @classmethod
    def load_from_yaml_string(cls, yaml_string: str) -> "GraphRules":
        """
        Load configuration from a YAML string and return an instance of
        GraphRules.
        """

        yaml_data = yaml.safe_load(yaml_string)
        return GraphRules(**yaml_data)
