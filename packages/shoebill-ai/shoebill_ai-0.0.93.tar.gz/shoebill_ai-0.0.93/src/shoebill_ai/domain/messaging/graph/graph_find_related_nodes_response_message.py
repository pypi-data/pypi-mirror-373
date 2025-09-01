from typing import TypeVar, Dict, Any, Type, List, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphFindRelatedNodesResponseMessage(HaiMessage):
    """Message containing related nodes found in the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, anchor_node: str, relationship_type: Optional[str], 
                       relationship_direction: Optional[str], nodes: List[Dict], 
                       relationships: List[Dict], success: bool = True, 
                       error_message: Optional[str] = None) -> 'GraphFindRelatedNodesResponseMessage':
        """Create a message with related nodes found in the graph"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_FIND_RELATED_NODES_RESPONSE,
            payload={
                "anchor_node": anchor_node,
                "relationship_type": relationship_type,
                "relationship_direction": relationship_direction,
                "nodes": nodes,
                "relationships": relationships,
                "success": success,
                "error_message": error_message
            },
        )

    @property
    def anchor_node(self) -> str:
        """Get the anchor node from the payload"""
        return self.payload.get("anchor_node", "")

    @property
    def relationship_type(self) -> Optional[str]:
        """Get the relationship type from the payload"""
        return self.payload.get("relationship_type")

    @property
    def relationship_direction(self) -> Optional[str]:
        """Get the relationship direction from the payload"""
        return self.payload.get("relationship_direction")

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
        """Get the success status from the payload"""
        return self.payload.get("success", False)

    @property
    def error_message(self) -> Optional[str]:
        """Get the error message from the payload if present"""
        return self.payload.get("error_message")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphFindRelatedNodesResponseMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            anchor_node=payload.get("anchor_node", ""),
            relationship_type=payload.get("relationship_type"),
            relationship_direction=payload.get("relationship_direction"),
            nodes=payload.get("nodes", []),
            relationships=payload.get("relationships", []),
            success=payload.get("success", False),
            error_message=payload.get("error_message")
        )