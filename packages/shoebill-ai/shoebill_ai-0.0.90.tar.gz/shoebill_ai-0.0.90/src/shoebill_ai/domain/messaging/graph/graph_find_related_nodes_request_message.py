from typing import TypeVar, Dict, Any, Type, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphFindRelatedNodesRequestMessage(HaiMessage):
    """Message to request finding related nodes in the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, anchor_node: str, relationship_type: str = None, 
                      relationship_direction: str = None, limit: int = None, 
                      traversal_depth: int = None) -> 'GraphFindRelatedNodesRequestMessage':
        """Create a message requesting to find related nodes in the graph"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_FIND_RELATED_NODES,
            payload={
                "anchor_node": anchor_node,
                "relationship_type": relationship_type,
                "relationship_direction": relationship_direction,
                "limit": limit,
                "traversal_depth": traversal_depth
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
    def limit(self) -> Optional[int]:
        """Get the limit from the payload"""
        return self.payload.get("limit")

    @property
    def traversal_depth(self) -> Optional[int]:
        """Get the traversal depth from the payload"""
        return self.payload.get("traversal_depth")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphFindRelatedNodesRequestMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload

        return cls.create_message(
            anchor_node=payload.get("anchor_node", ""),
            relationship_type=payload.get("relationship_type"),
            relationship_direction=payload.get("relationship_direction"),
            limit=payload.get("limit"),
            traversal_depth=payload.get("traversal_depth")
        )