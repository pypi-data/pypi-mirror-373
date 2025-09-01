from typing import TypeVar, Dict, Any, Type, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class GraphPathsRequestMessage(HaiMessage):
    """Message to request paths between nodes in the graph"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, 
                      source_node_id: str,
                      target_node_id: str,
                      relationship_type: Optional[str] = None,
                      path_type: Optional[str] = None) -> 'GraphPathsRequestMessage':
        """
        Create a message requesting to find paths between nodes in the graph
        
        Args:
            source_node_id: The ID of the source node
            target_node_id: The ID of the target node
            relationship_type: Optional type of relationship to traverse
            path_type: Optional type of path to find (shortest, all_shortest, all_info)
            
        Returns:
            A new GraphPathsRequestMessage
        """
        payload = {
            "source_node_id": source_node_id,
            "target_node_id": target_node_id,
        }
        
        if relationship_type:
            payload["relationship_type"] = relationship_type
            
        if path_type:
            payload["path_type"] = path_type
            
        return cls.create(
            topic=RequestMessageTopic.GRAPH_PATHS,
            payload=payload,
        )

    @property
    def source_node_id(self) -> str:
        """Get the source node ID from the payload"""
        return self.payload.get("source_node_id", "")
        
    @property
    def target_node_id(self) -> str:
        """Get the target node ID from the payload"""
        return self.payload.get("target_node_id", "")
        
    @property
    def relationship_type(self) -> Optional[str]:
        """Get the relationship type from the payload"""
        return self.payload.get("relationship_type")
        
    @property
    def path_type(self) -> Optional[str]:
        """Get the path type from the payload"""
        return self.payload.get("path_type")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphPathsRequestMessage':
        """Create a GraphPathsRequestMessage from a HaiMessage"""
        payload = message.payload
        source_node_id = payload.get("source_node_id", "")
        target_node_id = payload.get("target_node_id", "")
        relationship_type = payload.get("relationship_type")
        path_type = payload.get("path_type")

        return cls.create_message(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relationship_type=relationship_type,
            path_type=path_type
        )