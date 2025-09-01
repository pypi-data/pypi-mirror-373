from typing import TypeVar, Dict, Any, Type, List, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class GraphNodesByPropertyResponseMessage(HaiMessage):
    """Response message containing nodes with a specific property value and their relationships"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, property_name: str, property_value: any,
                       nodes: List[Dict], relationships: List[Dict],
                       success: bool = True, error_message: Optional[str] = None) -> 'GraphNodesByPropertyResponseMessage':
        """
        Create a response message with nodes having a specific property value and their relationships

        Args:
            property_name: The property name that was queried
            property_value: The property value that was queried
            nodes: List of node dictionaries
            relationships: List of relationship dictionaries
            success: Whether the operation was successful
            error_message: Error message if the operation failed

        Returns:
            A response message with the query results
        """
        return cls.create(
            topic=RequestMessageTopic.GRAPH_NODES_BY_PROPERTY_RESPONSE,
            payload={
                "property_name": property_name,
                "property_value": property_value,
                "nodes": nodes,
                "relationships": relationships,
                "success": success,
                "error_message": error_message
            },
        )

    @property
    def property_name(self) -> str:
        """Get the property name from the payload"""
        return self.payload.get("property_name")

    @property
    def property_value(self) -> any:
        """Get the property value from the payload"""
        return self.payload.get("property_value")

    @property
    def nodes(self) -> List[Dict]:
        """Get the list of nodes from the payload"""
        return self.payload.get("nodes", [])

    @property
    def relationships(self) -> List[Dict]:
        """Get the list of relationships from the payload"""
        return self.payload.get("relationships", [])

    @property
    def success(self) -> bool:
        """Check if the query was successful"""
        return self.payload.get("success", False)

    @property
    def error_message(self) -> Optional[str]:
        """Get the error message from the payload if present"""
        return self.payload.get("error_message")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphNodesByPropertyResponseMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            property_name=payload.get("property_name", ''),
            property_value=payload.get("property_value"),
            nodes=payload.get("nodes", []),
            relationships=payload.get("relationships", []),
            success=payload.get("success", False),
            error_message=payload.get("error_message")
        )
