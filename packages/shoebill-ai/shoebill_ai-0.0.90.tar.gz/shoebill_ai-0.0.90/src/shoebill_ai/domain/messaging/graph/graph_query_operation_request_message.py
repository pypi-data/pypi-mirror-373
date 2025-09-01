import json
from typing import Dict, Any, Type, TypeVar

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphQueryOperationRequestMessage(HaiMessage):
    """Message to request graph query operations"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls,
                       operation_type: str,
                       anchor_node: str,
                       relationship_direction: str = None,
                       relationship_type: str = None,
                       limit: int = None,
                       traversal_depth: int = None) -> 'GraphQueryOperationRequestMessage':
        """
        Create a message requesting a graph query operation

        Args:
            operation_type: One of 'FIND_RELATED_NODES', 'GET_NODE_INFO', 'COUNT_RELATIONSHIPS'
            anchor_node: The central node in the query (e.g., 'hyperliquid')
            relationship_direction: One of 'INCOMING', 'OUTGOING', or 'BOTH'
            relationship_type: The relationship type to traverse (e.g., 'BUILDS_ON')
            limit: Numerical limit of results to return
            traversal_depth: How many relationship hops to traverse

        Returns:
            A new GraphQueryOperationRequestMessage
        """
        # Build the query operation dictionary
        query_operation = {
            "operation_type": operation_type,
            "anchor_node": anchor_node,
        }

        # Add optional parameters if provided
        if relationship_direction is not None:
            query_operation["relationship_direction"] = relationship_direction

        if relationship_type is not None:
            query_operation["relationship_type"] = relationship_type

        if limit is not None:
            query_operation["limit"] = f"{limit}"

        if traversal_depth is not None:
            query_operation["traversal_depth"] = f"{traversal_depth}"

        return cls.create(
            topic=RequestMessageTopic.GRAPH_QUERY_OPERATION,
            payload={"query_operation": json.dumps(query_operation)},
        )

    @property
    def query_operation(self) -> Dict[str, Any]:
        """Get the query operation from the payload"""
        query_operation_payload = self.payload.get("query_operation", "{}")
        return json.loads(query_operation_payload)

    @property
    def operation_type(self) -> str:
        """Get the operation type from the query operation"""
        return self.query_operation.get("operation_type", "")

    @property
    def anchor_node(self) -> str:
        """Get the anchor node from the query operation"""
        return self.query_operation.get("anchor_node", "")

    @property
    def relationship_direction(self) -> str:
        """Get the relationship direction from the query operation"""
        return self.query_operation.get("relationship_direction", "BOTH")

    @property
    def relationship_type(self) -> str:
        """Get the relationship type from the query operation"""
        return self.query_operation.get("relationship_type", "")

    @property
    def limit(self) -> int:
        """Get the limit from the query operation"""
        return int(self.query_operation.get("limit", 10))

    @property
    def traversal_depth(self) -> int:
        """Get the traversal depth from the query operation"""
        return int(self.query_operation.get("traversal_depth", 1))

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphQueryOperationRequestMessage':
        """Create a GraphQueryOperationRequestMessage from a HaiMessage"""
        payload = message.payload
        query_operation_str = payload.get("query_operation", "{}")
        query_operation = json.loads(query_operation_str)

        return cls.create_message(
            operation_type=query_operation.get("operation_type", ""),
            anchor_node=query_operation.get("anchor_node", ""),
            relationship_direction=query_operation.get("relationship_direction"),
            relationship_type=query_operation.get("relationship_type"),
            limit=query_operation.get("limit"),
            traversal_depth=query_operation.get("traversal_depth")
        )