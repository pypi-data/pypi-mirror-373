from typing import TypeVar, Dict, Any, Type, List, Optional

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')


class GraphNodeSubgraphResponseMessage(HaiMessage):
    """Message containing a subgraph centered on a specific node"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls, node_id: str, announcements: List[Dict], claims: List[Dict], 
                       users: List[Dict], events: List[Dict], relationships: List[Dict], 
                       opinions: List[Dict], sources: List[Dict], tweets: List[Dict], 
                       entities: List[Dict], edges: List[Dict], central_node_id: str,
                       success: bool = True, error_message: Optional[str] = None) -> 'GraphNodeSubgraphResponseMessage':
        """Create a message with a subgraph centered on a specific node"""
        return cls.create(
            topic=RequestMessageTopic.GRAPH_NODE_SUBGRAPH_RESPONSE,
            payload={
                "node_id": node_id,
                "subgraph": {
                    "announcements": announcements,
                    "claims": claims,
                    "users": users,
                    "events": events,
                    "relationships": relationships,
                    "opinions": opinions,
                    "sources": sources,
                    "tweets": tweets,
                    "entities": entities,
                    "edges": edges,
                    "central_node_id": central_node_id
                },
                "success": success,
                "error_message": error_message
            },
        )

    @property
    def node_id(self) -> str:
        """Get the node ID from the payload"""
        return self.payload.get("node_id", "")

    @property
    def subgraph(self) -> Dict[str, Any]:
        """Get the subgraph from the payload"""
        return self.payload.get("subgraph", {})

    @property
    def announcements(self) -> List[Dict]:
        """Get the list of announcement nodes from the subgraph"""
        return self.subgraph.get("announcements", [])

    @property
    def claims(self) -> List[Dict]:
        """Get the list of claim nodes from the subgraph"""
        return self.subgraph.get("claims", [])

    @property
    def users(self) -> List[Dict]:
        """Get the list of user nodes from the subgraph"""
        return self.subgraph.get("users", [])

    @property
    def events(self) -> List[Dict]:
        """Get the list of event nodes from the subgraph"""
        return self.subgraph.get("events", [])

    @property
    def relationships(self) -> List[Dict]:
        """Get the list of relationship nodes from the subgraph"""
        return self.subgraph.get("relationships", [])

    @property
    def opinions(self) -> List[Dict]:
        """Get the list of opinion nodes from the subgraph"""
        return self.subgraph.get("opinions", [])

    @property
    def sources(self) -> List[Dict]:
        """Get the list of source nodes from the subgraph"""
        return self.subgraph.get("sources", [])

    @property
    def tweets(self) -> List[Dict]:
        """Get the list of tweet nodes from the subgraph"""
        return self.subgraph.get("tweets", [])

    @property
    def entities(self) -> List[Dict]:
        """Get the list of entity nodes from the subgraph"""
        return self.subgraph.get("entities", [])

    @property
    def edges(self) -> List[Dict]:
        """Get the list of edges from the subgraph"""
        return self.subgraph.get("edges", [])

    @property
    def central_node_id(self) -> str:
        """Get the central node ID from the subgraph"""
        return self.subgraph.get("central_node_id", "")

    @property
    def success(self) -> bool:
        """Get the success status from the payload"""
        return self.payload.get("success", False)

    @property
    def error_message(self) -> Optional[str]:
        """Get the error message from the payload if present"""
        return self.payload.get("error_message")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphNodeSubgraphResponseMessage':
        # Extract the necessary fields from the message payload
        payload = message.payload
        subgraph = payload.get("subgraph", {})

        return cls.create_message(
            node_id=payload.get("node_id", ""),
            announcements=subgraph.get("announcements", []),
            claims=subgraph.get("claims", []),
            users=subgraph.get("users", []),
            events=subgraph.get("events", []),
            relationships=subgraph.get("relationships", []),
            opinions=subgraph.get("opinions", []),
            sources=subgraph.get("sources", []),
            tweets=subgraph.get("tweets", []),
            entities=subgraph.get("entities", []),
            edges=subgraph.get("edges", []),
            central_node_id=subgraph.get("central_node_id", ""),
            success=payload.get("success", False),
            error_message=payload.get("error_message")
        )