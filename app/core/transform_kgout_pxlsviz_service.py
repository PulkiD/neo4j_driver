"""
Query Service Module.

This module contains the business logic for executing and processing Neo4j queries.
"""

from app.utils.logger import get_logger
from app.middleware.context import get_request_id
from typing import Any, Dict, List, Optional, Tuple, Set

# --- Configuration (can be kept separate or moved into the class as defaults) ---

# Default parameters for node and relationship tags
DEFAULT_PARAMS = {
    'source_node_tag': 'start',
    'target_node_tag': 'end',
    'relationship_type_tag': 'type'
}

# Properties to exclude from copying (source and target nodes are handled separately)
DEFAULT_EXCLUDED_PROPERTIES: Tuple[str, ...] = (
    "source",
    "target",
    "start",
    "end"
)

logger = get_logger()

def generate_relationship_id(
        start_id: str, rel_type: str, end_id: str
    ) -> str:
        """
        Generates a consistent ID for a relationship based on its components.

        Args:
            start_id: The ID of the source node.
            rel_type: The type of the relationship.
            end_id: The ID of the target node.

        Returns:
            A formatted string representing the relationship ID.
            Consider using UUIDs or hashing if simple concatenation might lead to
            collisions or contains characters problematic for downstream systems.
        """
        return f"{start_id}_{rel_type}_{end_id}"


class GraphTransformer:
    """
    Transforms input data containing relationship objects into a graph structure
    with unique nodes and formatted relationships (edges).

    Handles extraction of nodes, transformation of relationships, and ensures
    uniqueness of nodes and edges in the output.
    """

    def __init__(
        self,
        params: Optional[Dict[str, str]] = None
    ):
        """
        Initializes the GraphTransformer.

        Args:
            params: Optional dictionary containing configuration parameters:
                   - source_node_tag: Key for source node in relationships (default: 'start')
                   - target_node_tag: Key for target node in relationships (default: 'end')
                   - relationship_type_tag: Key for relationship type (default: 'type')
        """
        # Initialize parameters with defaults, update with any provided values
        self.params = DEFAULT_PARAMS.copy()
        if params:
            self.params.update(params)

        # State variables reset for each transformation run
        self._unique_nodes: Dict[str, Dict[str, Any]] = {}
        self._transformed_relationships: List[Dict[str, Any]] = []
        self._processed_rel_ids: Set[str] = set()
        self._total_rels_processed = 0
        self._skipped_rels = 0

    def _reset_state(self):
        """Resets internal state variables before processing new data."""
        self._unique_nodes = {}
        self._transformed_relationships = []
        self._processed_rel_ids = set()
        self._total_rels_processed = 0
        self._skipped_rels = 0
        logger.debug("Internal state reset for new transformation.")

    def _extract_node(
        self, node_data: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Validates and returns the node data if it's a dictionary containing an 'id'.

        Args:
            node_data: The potential node dictionary (e.g., from 'start' or 'end').

        Returns:
            The node dictionary if valid and contains an 'id', otherwise None.
        """
        if (
            isinstance(node_data, dict)
            and "id" in node_data
            and node_data["id"] is not None
        ):
            return node_data
        logger.debug(f"Invalid or incomplete node data encountered: {node_data}")
        return None


    def _extract_nodes_and_ids(
        self, rel_data: Dict[str, Any]
    ) -> Tuple[
        Optional[Dict[str, Any]], Optional[str], Optional[Dict[str, Any]], Optional[str]
    ]:
        """
        Extracts start and end node data and their IDs from a relationship dictionary.

        Args:
            rel_data: A dictionary representing a single relationship object.

        Returns:
            A tuple containing: (start_node, start_id, end_node, end_id).
            Node objects and IDs can be None if the data is missing or invalid.
        """
        start_node = self._extract_node(rel_data.get(self.params['source_node_tag']))
        end_node = self._extract_node(rel_data.get(self.params['target_node_tag']))

        start_id = start_node.get("id") if start_node else None
        end_id = end_node.get("id") if end_node else None

        return start_node, start_id, end_node, end_id

    def _transform_single_relationship(
        self, rel_data: Dict[str, Any], start_id: str, end_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Transforms a single input relationship object into the desired graph edge format.

        Args:
            rel_data: The original relationship dictionary from the input.
            start_id: The ID of the source node for this relationship.
            end_id: The ID of the target node for this relationship.

        Returns:
            A dictionary representing the transformed relationship (graph edge),
            or None if essential data (like 'type') is missing.
        """
        rel_type = rel_data.get(self.params['relationship_type_tag'])
        if not isinstance(rel_type, str) or not rel_type:
            logger.warning(
                "Relationship missing valid 'type'. Skipping transformation."
            )
            return None

        transformed_rel = {
            "id": generate_relationship_id(start_id, rel_type, end_id),
            "source": start_id,
            "target": end_id,
            # Ensure type is always present
            "type": rel_type,
        }

        # Copy all properties except source/target node tags and other excluded properties
        excluded_properties = {
            self.params['source_node_tag'],
            self.params['target_node_tag'],
            *DEFAULT_EXCLUDED_PROPERTIES
        }

        # Copy all properties that aren't in the excluded set
        for key, value in rel_data.items():
            if key not in excluded_properties:
                transformed_rel[key] = value

        return transformed_rel

    def transform_data(
        self, source_data: List[Dict[str, Dict[str, Any]]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Transforms input data into a graph structure (nodes and relationships).

        The input is expected to be a list of dictionaries. Each dictionary in the
        list contains arbitrary keys (e.g., "rel", "rel1"), where each *value*
        associated with these keys is a complete relationship object dictionary
        (containing 'start', 'end', 'type', etc.).

        Args:
            source_data: A list of dictionaries, where each inner dictionary's
                         values are the relationship objects to process.

        Returns:
            A dictionary with two keys:
            'nodes': A list of unique node dictionaries found in the relationships.
            'relationships': A list of transformed relationship dictionaries (edges).
                             Returns empty lists if input is invalid or no valid
                             relationships are found.
        """
        self._reset_state()  # Ensure clean state for this run

        if not isinstance(source_data, list):
            logger.error(
                "Invalid input: Input data must be a list. Returning empty graph."
            )
            return {"nodes": [], "relationships": []}

        for (
            item_dict
        ) in source_data:  # Iterate through the list [ {rel_key: rel_obj,...}, ...]
            if not isinstance(item_dict, dict):
                logger.warning(
                    f"Skipping non-dictionary item in outer list: {type(item_dict)}"
                )
                self._skipped_rels += 1  # Count this as a skipped potential source
                continue

            for (
                rel_key,
                rel_data,
            ) in item_dict.items():  # Iterate through {"rel_key": rel_obj} pairs
                if not isinstance(rel_data, dict):
                    logger.warning(
                        f"Skipping non-dictionary value for key '{rel_key}'. Expected relationship object."
                    )
                    self._skipped_rels += 1
                    continue

                self._total_rels_processed += 1
                start_node, start_id, end_node, end_id = self._extract_nodes_and_ids(
                    rel_data
                )

                # Validate extracted nodes and IDs are present
                if not (start_node and start_id and end_node and end_id):
                    rel_type_info = rel_data.get("type", "N/A")
                    logger.warning(
                        f"Skipping relationship (type: {rel_type_info}, key: {rel_key}) due to missing/invalid node data or ID."
                    )
                    self._skipped_rels += 1
                    continue

                # Add nodes to dictionary (handles uniqueness by ID)
                if start_id not in self._unique_nodes:
                    self._unique_nodes[start_id] = start_node
                    logger.debug(f"Added new node: {start_id}")
                if end_id not in self._unique_nodes:
                    self._unique_nodes[end_id] = end_node
                    logger.debug(f"Added new node: {end_id}")

                # Transform the relationship object into the edge format
                transformed_rel = self._transform_single_relationship(
                    rel_data, start_id, end_id
                )

                if transformed_rel:
                    rel_output_id = transformed_rel["id"]
                    # Add relationship only if it hasn't been processed before
                    if rel_output_id not in self._processed_rel_ids:
                        self._transformed_relationships.append(transformed_rel)
                        self._processed_rel_ids.add(rel_output_id)
                        logger.debug(f"Added new relationship: {rel_output_id}")
                    else:
                        logger.info(
                            f"Skipping duplicate relationship ID encountered: {rel_output_id}"
                        )
                        # Note: Assumes ID generation is deterministic and sufficient.
                else:
                    # _transform_single_relationship already logged the reason
                    self._skipped_rels += 1

        logger.info(
            f"Attempted to process {self._total_rels_processed} relationship objects from input."
        )
        logger.info(
            f"Successfully extracted {len(self._unique_nodes)} unique nodes."
        )
        logger.info(
            f"Successfully created {len(self._transformed_relationships)} unique output relationships."
        )
        if self._skipped_rels > 0:
            logger.warning(
                f"Skipped {self._skipped_rels} relationship objects due to validation errors or missing data."
            )

        return {
            "nodes": list(self._unique_nodes.values()),
            "relationships": self._transformed_relationships,
        }


class TransformKGOutPxLSVizService:
    """Service class for handling Neo4j query operations."""

    @staticmethod
    async def transform_to_pxlsviz(input_json: list, params: dict = None):
        """
        Execute a Cypher query and format the results.

        Args:
            input_json (list): The Cypher query output to be transformed
            params (dict, optional): Parameters for the transformation. Defaults to None.
                Supported parameters:
                - source_node_tag: Key for source node in relationships (default: 'start')
                - target_node_tag: Key for target node in relationships (default: 'end')
                - relationship_type_tag: Key for relationship type (default: 'type')

        Returns:
            Dict: A dictionary containing transformed nodes and relationships

        Raises:
            Exception: If there's an error executing the transformation
        """
        request_id = get_request_id()
        try:
            # Create an instance of the transformer with provided or default parameters
            transformer = GraphTransformer(params)

            # Perform the transformation
            graph_output = transformer.transform_data(input_json)

            logger.info(
                "Transformation executed successfully.",
                extra={"request_id": request_id},
            )

            return graph_output

        except Exception as e:
            logger.error(
                f"Error executing transformation to PxLSViz format: {str(e)}",
                extra={"request_id": request_id, "error": str(e)},
            )
            raise
