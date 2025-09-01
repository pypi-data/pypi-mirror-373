import json
from typing import TypeVar, Dict, Any, Type, List, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class GraphPathsResponseMessage(HaiMessage):
    """Message with results from graph path finding operations"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls,
                       source_node_id: str,
                       target_node_id: str,
                       paths: List[Any],
                       path_type: str,
                       success: bool = True,
                       error_message: Optional[str] = None) -> 'GraphPathsResponseMessage':
        """
        Create a response message with graph path finding results
        
        Args:
            source_node_id: The ID of the source node
            target_node_id: The ID of the target node
            paths: List of paths found between the nodes
            path_type: Type of path that was requested (shortest, all_shortest, all_info)
            success: Whether the operation was successful
            error_message: Error message if the operation failed
            
        Returns:
            A new GraphPathsResponseMessage
        """
        payload = {
            "source_node_id": source_node_id,
            "target_node_id": target_node_id,
            "paths": json.dumps(paths),
            "path_type": path_type,
            "success": success
        }
        
        if error_message:
            payload["error_message"] = error_message
            
        return cls.create(
            topic=RequestMessageTopic.GRAPH_PATHS_RESPONSE,
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
    def paths(self) -> List[Any]:
        """Get the paths from the payload"""
        paths_str = self.payload.get("paths", "[]")
        return json.loads(paths_str)
        
    @property
    def path_type(self) -> str:
        """Get the path type from the payload"""
        return self.payload.get("path_type", "")
        
    @property
    def success(self) -> bool:
        """Get the success status from the payload"""
        return self.payload.get("success", False)
        
    @property
    def error_message(self) -> str:
        """Get the error message from the payload"""
        return self.payload.get("error_message", "")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphPathsResponseMessage':
        """Create a GraphPathsResponseMessage from a HaiMessage"""
        payload = message.payload
        source_node_id = payload.get("source_node_id", "")
        target_node_id = payload.get("target_node_id", "")
        paths_str = payload.get("paths", "[]")
        paths = json.loads(paths_str)
        path_type = payload.get("path_type", "")
        success = payload.get("success", False)
        error_message = payload.get("error_message")
        
        return cls.create_message(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            paths=paths,
            path_type=path_type,
            success=success,
            error_message=error_message
        )