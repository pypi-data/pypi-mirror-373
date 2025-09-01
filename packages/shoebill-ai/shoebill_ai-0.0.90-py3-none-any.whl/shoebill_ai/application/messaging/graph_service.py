import logging
from typing import Optional, Any, Dict, List

from h_message_bus import NatsPublisherAdapter

from ...domain.messaging.graph.graph_clear_request_message import GraphClearRequestMessage
from ...domain.messaging.graph.graph_count_relationships_request_message import GraphCountRelationshipsRequestMessage
from ...domain.messaging.graph.graph_count_relationships_response_message import GraphCountRelationshipsResponseMessage
from ...domain.messaging.graph.graph_find_related_nodes_request_message import GraphFindRelatedNodesRequestMessage
from ...domain.messaging.graph.graph_find_related_nodes_response_message import GraphFindRelatedNodesResponseMessage
from ...domain.messaging.graph.graph_get_all_request_message import GraphGetAllRequestMessage
from ...domain.messaging.graph.graph_get_all_result_response_message import GraphGetAllResultResponseMessage
from ...domain.messaging.graph.graph_incoming_relationships_request_message import \
    GraphIncomingRelationshipsRequestMessage
from ...domain.messaging.graph.graph_incoming_relationships_response_message import \
    GraphIncomingRelationshipsResponseMessage
from ...domain.messaging.graph.graph_node_add_request_message import GraphNodeAddRequestMessage
from ...domain.messaging.graph.graph_node_get_request_message import GraphNodeGetRequestMessage
from ...domain.messaging.graph.graph_node_get_result_response_message import GraphNodeGetResultResponseMessage
from ...domain.messaging.graph.graph_node_info_request_message import GraphNodeInfoRequestMessage
from ...domain.messaging.graph.graph_node_info_response_message import GraphNodeInfoResponseMessage
from ...domain.messaging.graph.graph_node_update_request_message import GraphNodeUpdateRequestMessage
from ...domain.messaging.graph.graph_node_update_response_message import GraphNodeUpdateResponseMessage
from ...domain.messaging.graph.graph_nodes_by_label_request_message import GraphNodesByLabelRequestMessage
from ...domain.messaging.graph.graph_nodes_by_label_response_message import GraphNodesByLabelResponseMessage
from ...domain.messaging.graph.graph_nodes_by_property_request_message import GraphNodesByPropertyRequestMessage
from ...domain.messaging.graph.graph_nodes_by_property_response_message import GraphNodesByPropertyResponseMessage
from ...domain.messaging.graph.graph_outgoing_relationships_request_message import \
    GraphOutgoingRelationshipsRequestMessage
from ...domain.messaging.graph.graph_outgoing_relationships_response_message import \
    GraphOutgoingRelationshipsResponseMessage
from ...domain.messaging.graph.graph_query_operation_request_message import GraphQueryOperationRequestMessage
from ...domain.messaging.graph.graph_query_operation_response_message import GraphQueryOperationResponseMessage
from ...domain.messaging.graph.graph_query_request_message import GraphQueryRequestMessage
from ...domain.messaging.graph.graph_relationship_added_request_message import GraphRelationshipAddRequestMessage
from ...domain.messaging.graph.graph_relationships_between_nodes_request_message import \
    GraphRelationshipsBetweenNodesRequestMessage
from ...domain.messaging.graph.graph_relationships_between_nodes_response_message import \
    GraphRelationshipsBetweenNodesResponseMessage
from ...domain.messaging.graph.graph_relationships_by_type_request_message import GraphRelationshipsByTypeRequestMessage
from ...domain.messaging.graph.graph_relationships_by_type_response_message import \
    GraphRelationshipsByTypeResponseMessage
from ...domain.messaging.graph.graph_paths_request_message import GraphPathsRequestMessage
from ...domain.messaging.graph.graph_paths_response_message import GraphPathsResponseMessage
from ...domain.messaging.graph.graph_announcement_nodes_since_timestamp_request_message import GraphAnnouncementNodesSinceTimestampRequestMessage
from ...domain.messaging.graph.graph_announcement_nodes_since_timestamp_response_message import GraphAnnouncementNodesSinceTimestampResponseMessage
from ...domain.messaging.graph.graph_event_nodes_since_timestamp_request_message import GraphEventNodesSinceTimestampRequestMessage
from ...domain.messaging.graph.graph_event_nodes_since_timestamp_response_message import GraphEventNodesSinceTimestampResponseMessage
from ...domain.messaging.graph.graph_opinion_nodes_since_timestamp_request_message import GraphOpinionNodesSinceTimestampRequestMessage
from ...domain.messaging.graph.graph_opinion_nodes_since_timestamp_response_message import GraphOpinionNodesSinceTimestampResponseMessage
from ...domain.messaging.graph.graph_node_subgraph_request_message import GraphNodeSubgraphRequestMessage
from ...domain.messaging.graph.graph_node_subgraph_response_message import GraphNodeSubgraphResponseMessage
from ...domain.messaging.graph.graph_find_opinions_on_node_request_message import GraphFindOpinionsOnNodeRequestMessage
from ...domain.messaging.graph.graph_find_opinions_on_node_response_message import GraphFindOpinionsOnNodeResponseMessage
from ...domain.messaging.graph.graph_find_relations_between_entities_request_message import GraphFindRelationsBetweenEntitiesRequestMessage
from ...domain.messaging.graph.graph_find_relations_between_entities_response_message import GraphFindRelationsBetweenEntitiesResponseMessage
from ...domain.messaging.graph.graph_trace_claim_source_request_message import GraphTraceClaimSourceRequestMessage
from ...domain.messaging.graph.graph_trace_claim_source_response_message import GraphTraceClaimSourceResponseMessage
from ...domain.messaging.graph.graph_trace_node_source_request_message import GraphTraceNodeSourceRequestMessage
from ...domain.messaging.graph.graph_trace_node_source_response_message import GraphTraceNodeSourceResponseMessage
from ...domain.messaging.graph.graph_find_user_events_and_announcements_request_message import GraphFindUserEventsAndAnnouncementsRequestMessage
from ...domain.messaging.graph.graph_find_user_events_and_announcements_response_message import GraphFindUserEventsAndAnnouncementsResponseMessage
from ...domain.messaging.graph.graph_get_statistics_request_message import GraphGetStatisticsRequestMessage
from ...domain.messaging.graph.graph_get_statistics_response_message import GraphGetStatisticsResponseMessage


class GraphService:
    def __init__(self, nats_publisher_adapter: NatsPublisherAdapter):
        self.nats_publisher_adapter = nats_publisher_adapter
        self.logger = logging.getLogger(__name__)

    async def query_operation(self, operation_type: str,
                              anchor_node: str,
                              relationship_type: str = None,
                              relationship_direction: str = None,
                              limit: int = None,
                              traversal_depth: int = None,
                              timeout: float = 30.0
                              ) -> Optional[Dict[str, Any]]:
        try:
            # Create the request message
            request_message = GraphQueryOperationRequestMessage.create_message(
                operation_type=operation_type,
                anchor_node=anchor_node,
                relationship_type=relationship_type,
                relationship_direction=relationship_direction,
                limit=limit,
                traversal_depth=traversal_depth
            )

            # Send the request and await the response
            response = await self.nats_publisher_adapter.request(
                request_message,
                timeout=timeout
            )

            # Parse the response
            if response:
                response_message = GraphQueryOperationResponseMessage.from_hai_message(response)

                if response_message.success:
                    #self.logger.info(f"Successfully processed {operation_type} operation for node '{anchor_node}'")
                    return response_message.result
                else:
                    self.logger.error(f"Error processing {operation_type} operation: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for {operation_type} operation (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Failed to send or process {operation_type} operation: {str(e)}")
            return None

    async def get_all_nodes(self, timeout: float = 30.0):
        try:
            # Create a request to get all nodes
            request = GraphGetAllRequestMessage.create_message()

            # Publish the request and await the response
            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            alldata=GraphGetAllResultResponseMessage.from_hai_message(response)
            #print(alldata.nodes)
            return alldata.nodes

        except Exception as e:
            self.logger.error(f"Error creating documents from graph nodes: {str(e)}")
            return 0

    async def add_node(self, node_id: str, labels: List[str], description: str, properties: dict[str, str]):
        try:
            request = GraphNodeAddRequestMessage.create_message(
                node_id=node_id,
                labels=labels,
                properties=properties,
                description=description)

            await self.nats_publisher_adapter.publish(request)

        except Exception as e:
            self.logger.error(f"Error adding node: {str(e)}")

    async def add_relation(self, source_node_id: str, target_node_id: str, relationship: str):
        try:
            request = GraphRelationshipAddRequestMessage.create_message(
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                relationship_type=relationship)

            await self.nats_publisher_adapter.publish(request)
        except Exception as e:
            self.logger.error(f"Error adding relation: {str(e)}")

    async def clear_graph(self, timeout: float = 30.0) -> bool:
        """Clear all nodes and relationships from the graph"""
        try:
            request = GraphClearRequestMessage.create_message()
            await self.nats_publisher_adapter.publish(request)
            #self.logger.info("Graph clear request sent")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing graph: {str(e)}")
            return False

    async def count_relationships(self, anchor_node: str, timeout: float = 30.0) -> Optional[int]:
        """Count relationships for a specific node"""
        try:
            request = GraphCountRelationshipsRequestMessage.create_message(
                anchor_node=anchor_node
            )

            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphCountRelationshipsResponseMessage.from_hai_message(response)
                if response_message.success:
                    #self.logger.info(f"Successfully counted relationships for node '{anchor_node}'")
                    return response_message.count
                else:
                    self.logger.error(f"Error counting relationships: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for count_relationships (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error counting relationships: {str(e)}")
            return None

    async def find_related_nodes(self, anchor_node: str, relationship_type: str = None, 
                                relationship_direction: str = None, limit: int = 10, traversal_depth: int = 3, timeout: float = 30.0) -> Optional[List[Dict[str, Any]]]:
        """Find nodes related to the anchor node"""
        try:
            request = GraphFindRelatedNodesRequestMessage.create_message(
                anchor_node=anchor_node,
                relationship_type=relationship_type,
                relationship_direction=relationship_direction,
                traversal_depth=traversal_depth,
                limit=limit,
            )

            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphFindRelatedNodesResponseMessage.from_hai_message(response)
                if response_message.success:
                    #self.logger.info(f"Successfully found related nodes for '{anchor_node}'")
                    return response_message.nodes
                else:
                    self.logger.error(f"Error finding related nodes: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for find_related_nodes (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error finding related nodes: {str(e)}")
            return None

    async def get_node(self, node_id: str, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Get a specific node by ID"""
        try:
            request = GraphNodeGetRequestMessage.create_message(
                node_id=node_id
            )

            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphNodeGetResultResponseMessage.from_hai_message(response)
                if response_message.found:
                    #self.logger.info(f"Successfully retrieved node '{node_id}'")
                    return {
                        "description":  response_message.description,
                        "id": response_message.node_id,
                        "labels": response_message.labels,
                        "properties": response_message.properties,
                    }
                else:
                    self.logger.error(f"Error retrieving node: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for get_node (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error retrieving node: {str(e)}")
            return None

    async def get_node_info(self, node_name: str, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Get information about a specific node"""
        try:
            request = GraphNodeInfoRequestMessage.create_message(
                node_name=node_name
            )

            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphNodeInfoResponseMessage.from_hai_message(response)
                if response_message.success:
                    #self.logger.info(f"Successfully retrieved info for node '{node_name}'")
                    return response_message.node_info
                else:
                    self.logger.error(f"Error retrieving node info: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for get_node_info (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error retrieving node info: {str(e)}")
            return None

    async def update_node(self, node_id: str, properties: Dict[str, Any], timeout: float = 30.0) -> bool:
        """Update a node's properties"""
        try:
            request = GraphNodeUpdateRequestMessage.create_message(
                node_id=node_id,
                properties=properties
            )

            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphNodeUpdateResponseMessage.from_hai_message(response)
                if response_message.success:
                    #self.logger.info(f"Successfully updated node '{node_id}'")
                    return True
                else:
                    self.logger.error(f"Error updating node: {response_message.error_message}")
                    return False
            else:
                self.logger.warning(f"No response received for update_node (timeout: {timeout}s)")
                return False

        except Exception as e:
            self.logger.error(f"Error updating node: {str(e)}")
            return False

    async def get_nodes_by_label(self, label: str, timeout: float = 30.0) -> Optional[List[Dict[str, Any]]]:
        """Get nodes by label"""
        try:
            request = GraphNodesByLabelRequestMessage.create_message(
                label=label
            )

            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphNodesByLabelResponseMessage.from_hai_message(response)
                if response_message.success:
                    #self.logger.info(f"Successfully retrieved nodes with label '{label}'")
                    return response_message.nodes
                else:
                    self.logger.error(f"Error retrieving nodes by label: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for get_nodes_by_label (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error retrieving nodes by label: {str(e)}")
            return None

    async def get_nodes_by_property(self, property_name: str, property_value: Any, timeout: float = 30.0) -> Optional[List[Dict[str, Any]]]:
        """Get nodes by property name and value"""
        try:
            request = GraphNodesByPropertyRequestMessage.create_message(
                property_name=property_name,
                property_value=property_value
            )

            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphNodesByPropertyResponseMessage.from_hai_message(response)
                if response_message.success:
                    #self.logger.info(f"Successfully retrieved nodes with property '{property_name}={property_value}'")
                    return response_message.nodes
                else:
                    self.logger.error(f"Error retrieving nodes by property: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for get_nodes_by_property (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error retrieving nodes by property: {str(e)}")
            return None

    async def get_announcement_nodes_since_timestamp(self, timestamp: str, timeout: float = 30.0) -> Optional[List[Dict[str, Any]]]:
        """Get announcement nodes since a specific timestamp"""
        try:
            request = GraphAnnouncementNodesSinceTimestampRequestMessage.create_message(
                timestamp_str=timestamp
            )

            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphAnnouncementNodesSinceTimestampResponseMessage.from_hai_message(response)
                if response_message.success:
                    #self.logger.info(f"Successfully retrieved announcement nodes since timestamp '{timestamp}'")
                    return response_message.announcement_nodes
                else:
                    self.logger.error(f"Error retrieving announcement nodes: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for get_announcement_nodes_since_timestamp (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error retrieving announcement nodes: {str(e)}")
            return None

    async def get_event_nodes_since_timestamp(self, timestamp: str, timeout: float = 30.0) -> Optional[List[Dict[str, Any]]]:
        """Get event nodes since a specific timestamp"""
        try:
            request = GraphEventNodesSinceTimestampRequestMessage.create_message(
                timestamp_str=timestamp
            )

            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphEventNodesSinceTimestampResponseMessage.from_hai_message(response)
                if response_message.success:
                    #self.logger.info(f"Successfully retrieved event nodes since timestamp '{timestamp}'")
                    return response_message.event_nodes
                else:
                    self.logger.error(f"Error retrieving event nodes: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for get_event_nodes_since_timestamp (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error retrieving event nodes: {str(e)}")
            return None

    async def get_opinion_nodes_since_timestamp(self, timestamp: str, timeout: float = 30.0) -> Optional[List[Dict[str, Any]]]:
        """Get opinion nodes since a specific timestamp"""
        try:
            request = GraphOpinionNodesSinceTimestampRequestMessage.create_message(
                timestamp_str=timestamp
            )
            self.logger.debug(f"Requesting opinions since timestamp '{request}'")
            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphOpinionNodesSinceTimestampResponseMessage.from_hai_message(response)
                if response_message.success:
                    #self.logger.info(f"Successfully retrieved opinion nodes since timestamp '{timestamp}'")
                    return response_message.opinion_nodes
                else:
                    self.logger.error(f"Error retrieving opinion nodes: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for get_opinion_nodes_since_timestamp (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error retrieving opinion nodes: {str(e)}")
            return None

    async def get_node_subgraph(self, node_id: str, max_traversal: int = 2, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Get a subgraph centered on a specific node"""
        try:
            request = GraphNodeSubgraphRequestMessage.create_message(
                node_id=node_id,
                max_traversal=max_traversal
            )

            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphNodeSubgraphResponseMessage.from_hai_message(response)
                if response_message.success:
                    #self.logger.info(f"Successfully retrieved subgraph for node '{node_id}'")
                    return {
                        "announcements": response_message.announcements,
                        "claims": response_message.claims,
                        "users": response_message.users,
                        "events": response_message.events,
                        "relationships": response_message.relationships,
                        "opinions": response_message.opinions,
                        "sources": response_message.sources,
                        "tweets": response_message.tweets,
                        "entities": response_message.entities,
                        "edges": response_message.edges,
                        "central_node_id": response_message.central_node_id
                    }
                else:
                    self.logger.error(f"Error retrieving subgraph: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for get_node_subgraph (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error retrieving subgraph: {str(e)}")
            return None

    async def find_opinions_on_node(self, node_id: str, since_timestamp: str = None, timeout: float = 30.0) -> Optional[List[Dict[str, Any]]]:
        """Find opinions on a specific node"""
        try:
            request = GraphFindOpinionsOnNodeRequestMessage.create_message(
                node_id=node_id,
                since_timestamp=since_timestamp
            )

            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphFindOpinionsOnNodeResponseMessage.from_hai_message(response)
                if response_message.success:
                    #self.logger.info(f"Successfully found opinions on node '{node_id}'")
                    return response_message.opinion_nodes
                else:
                    self.logger.error(f"Error finding opinions on node: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for find_opinions_on_node (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error finding opinions on node: {str(e)}")
            return None

    async def find_relations_between_entities(self, entity1_id: str, entity2_id: str, timeout: float = 30.0) -> Optional[List[Dict[str, Any]]]:
        """Find relations between two entities"""
        try:
            request = GraphFindRelationsBetweenEntitiesRequestMessage.create_message(
                entity1_id=entity1_id,
                entity2_id=entity2_id
            )

            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphFindRelationsBetweenEntitiesResponseMessage.from_hai_message(response)
                if response_message.success:
                    #self.logger.info(f"Successfully found relations between entities '{entity1_id}' and '{entity2_id}'")
                    return response_message.paths
                else:
                    self.logger.error(f"Error finding relations between entities: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for find_relations_between_entities (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error finding relations between entities: {str(e)}")
            return None

    async def trace_claim_source(self, claim_node_id: str, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Trace the source of a claim node"""
        try:
            request = GraphTraceClaimSourceRequestMessage.create_message(
                claim_node_id=claim_node_id
            )

            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphTraceClaimSourceResponseMessage.from_hai_message(response)
                if response_message.success:
                    #self.logger.info(f"Successfully traced source of claim node '{claim_node_id}'")
                    return response_message.source_node
                else:
                    self.logger.error(f"Error tracing source of claim node: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for trace_claim_source (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error tracing source of claim node: {str(e)}")
            return None

    async def trace_node_source(self, node_id: str, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Trace the source of a node"""
        try:
            request = GraphTraceNodeSourceRequestMessage.create_message(
                node_id=node_id
            )

            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphTraceNodeSourceResponseMessage.from_hai_message(response)
                if response_message.success:
                    #self.logger.info(f"Successfully traced source of node '{node_id}'")
                    return response_message.source_node
                else:
                    self.logger.error(f"Error tracing source of node: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for trace_node_source (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error tracing source of node: {str(e)}")
            return None

    async def find_user_events_and_announcements(self, user_node_id: str, timeout: float = 30.0) -> Optional[Dict[str, List[Dict[str, Any]]]]:
        """Find events and announcements associated with a user"""
        try:
            request = GraphFindUserEventsAndAnnouncementsRequestMessage.create_message(
                user_node_id=user_node_id
            )

            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphFindUserEventsAndAnnouncementsResponseMessage.from_hai_message(response)
                if response_message.success:
                    #self.logger.info(f"Successfully found events and announcements for user '{user_node_id}'")
                    return {
                        "announcements": response_message.announcements,
                        "events": response_message.events
                    }
                else:
                    self.logger.error(f"Error finding events and announcements for user: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for find_user_events_and_announcements (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error finding events and announcements for user: {str(e)}")
            return None

    async def get_graph_statistics(self, timeout: float = 30.0) -> Optional[Dict[str, int]]:
        """Get statistics from the graph"""
        try:
            request = GraphGetStatisticsRequestMessage.create_message()

            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphGetStatisticsResponseMessage.from_hai_message(response)
                if response_message.success:
                    #self.logger.info("Successfully retrieved graph statistics")
                    return response_message.statistics
                else:
                    self.logger.error(f"Error retrieving graph statistics: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for get_graph_statistics (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error retrieving graph statistics: {str(e)}")
            return None

    async def get_incoming_relationships(self, node_id: str, timeout: float = 30.0) -> Optional[List[Dict[str, Any]]]:
        """Get incoming relationships for a node"""
        try:
            request = GraphIncomingRelationshipsRequestMessage.create_message(
                node_id=node_id
            )

            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphIncomingRelationshipsResponseMessage.from_hai_message(response)
                if response_message.success:
                    #self.logger.info(f"Successfully retrieved incoming relationships for node '{node_id}'")
                    return response_message.relationships
                else:
                    self.logger.error(f"Error retrieving incoming relationships: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for get_incoming_relationships (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error retrieving incoming relationships: {str(e)}")
            return None

    async def get_outgoing_relationships(self, node_id: str, timeout: float = 30.0) -> Optional[List[Dict[str, Any]]]:
        """Get outgoing relationships for a node"""
        try:
            request = GraphOutgoingRelationshipsRequestMessage.create_message(
                node_id=node_id
            )

            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphOutgoingRelationshipsResponseMessage.from_hai_message(response)
                if response_message.success:
                    #self.logger.info(f"Successfully retrieved outgoing relationships for node '{node_id}'")
                    return response_message.relationships
                else:
                    self.logger.error(f"Error retrieving outgoing relationships: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for get_outgoing_relationships (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error retrieving outgoing relationships: {str(e)}")
            return None

    async def get_relationships_between_nodes(self, source_node_id: str, target_node_id: str, timeout: float = 30.0) -> Optional[List[Dict[str, Any]]]:
        """Get relationships between two nodes"""
        try:
            request = GraphRelationshipsBetweenNodesRequestMessage.create_message(
                source_node_id=source_node_id,
                target_node_id=target_node_id
            )

            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphRelationshipsBetweenNodesResponseMessage.from_hai_message(response)
                if response_message.success:
                    #self.logger.info(f"Successfully retrieved relationships between nodes '{source_node_id}' and '{target_node_id}'")
                    return response_message.relationships
                else:
                    self.logger.error(f"Error retrieving relationships between nodes: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for get_relationships_between_nodes (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error retrieving relationships between nodes: {str(e)}")
            return None

    async def get_relationships_by_type(self, relationship_type: str, timeout: float = 30.0) -> Optional[List[Dict[str, Any]]]:
        """Get relationships by type"""
        try:
            request = GraphRelationshipsByTypeRequestMessage.create_message(
                relationship_type=relationship_type
            )

            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphRelationshipsByTypeResponseMessage.from_hai_message(response)
                if response_message.success:
                    #self.logger.info(f"Successfully retrieved relationships of type '{relationship_type}'")
                    return response_message.relationships
                else:
                    self.logger.error(f"Error retrieving relationships by type: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for get_relationships_by_type (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error retrieving relationships by type: {str(e)}")
            return None

    async def execute_query(self, query: str, parameters: Dict[str, Any] = None, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Execute a custom query against the graph database"""
        try:
            request = GraphQueryRequestMessage.create_message(
                query=query,
                parameters=parameters or {}
            )

            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                # Since there's no specific response message for GraphQueryRequestMessage,
                # we'll assume the response follows the standard pattern
                if response.payload.get("success", False):
                    #self.logger.info(f"Successfully executed custom query")
                    return response.payload.get("result", {})
                else:
                    self.logger.error(f"Error executing custom query: {response.payload.get('error_message', 'Unknown error')}")
                    return None
            else:
                self.logger.warning(f"No response received for execute_query (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error executing custom query: {str(e)}")
            return None

    async def find_shortest_path(self, source_node_id: str, target_node_id: str, relationship_type: str = None, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """
        Find the shortest path between two nodes in the graph

        Args:
            source_node_id: ID of the source node
            target_node_id: ID of the target node
            relationship_type: Optional type of relationship to traverse
            timeout: Request timeout in seconds

        Returns:
            Dictionary representing the path if found, None otherwise
        """
        try:
            # Create the request message
            request = GraphPathsRequestMessage.create_message(
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                relationship_type=relationship_type,
                path_type="shortest"
            )

            # Send the request and await the response
            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphPathsResponseMessage.from_hai_message(response)
                if response_message.success:
                    paths = response_message.paths
                    if paths and len(paths) > 0:
                        #self.logger.info(f"Successfully found shortest path from '{source_node_id}' to '{target_node_id}'")
                        return paths[0]  # Return the first (and only) path
                    else:
                        self.logger.info(f"No path found from '{source_node_id}' to '{target_node_id}'")
                        return None
                else:
                    self.logger.error(f"Error finding shortest path: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for find_shortest_path (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error finding shortest path: {str(e)}")
            return None

    async def find_all_shortest_paths(self, source_node_id: str, target_node_id: str, relationship_type: str = None, timeout: float = 30.0) -> Optional[List[Dict[str, Any]]]:
        """
        Find all shortest paths between two nodes in the graph

        Args:
            source_node_id: ID of the source node
            target_node_id: ID of the target node
            relationship_type: Optional type of relationship to traverse
            timeout: Request timeout in seconds

        Returns:
            List of dictionaries representing the paths if found, None otherwise
        """
        try:
            # Create the request message
            request = GraphPathsRequestMessage.create_message(
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                relationship_type=relationship_type,
                path_type="all_shortest"
            )

            # Send the request and await the response
            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphPathsResponseMessage.from_hai_message(response)
                if response_message.success:
                    paths = response_message.paths
                    if paths and len(paths) > 0:
                        #self.logger.info(f"Successfully found {len(paths)} shortest paths from '{source_node_id}' to '{target_node_id}'")
                        return paths
                    else:
                        #self.logger.info(f"No paths found from '{source_node_id}' to '{target_node_id}'")
                        return []
                else:
                    self.logger.error(f"Error finding all shortest paths: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for find_all_shortest_paths (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error finding all shortest paths: {str(e)}")
            return None

    async def find_path_with_all_info(self, source_node_id: str, target_node_id: str, relationship_type: str = None, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """
        Find a path between two nodes with all information included

        Args:
            source_node_id: ID of the source node
            target_node_id: ID of the target node
            relationship_type: Optional type of relationship to traverse
            timeout: Request timeout in seconds

        Returns:
            Dictionary representing the path with all information if found, None otherwise
        """
        try:
            # Create the request message
            request = GraphPathsRequestMessage.create_message(
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                relationship_type=relationship_type,
                path_type="all_info"
            )

            # Send the request and await the response
            response = await self.nats_publisher_adapter.request(request, timeout=timeout)

            if response:
                response_message = GraphPathsResponseMessage.from_hai_message(response)
                if response_message.success:
                    paths = response_message.paths
                    if paths and len(paths) > 0:
                        #self.logger.info(f"Successfully found path with all info from '{source_node_id}' to '{target_node_id}'")
                        return paths[0]  # Return the first (and only) path
                    else:
                        #self.logger.info(f"No path found from '{source_node_id}' to '{target_node_id}'")
                        return None
                else:
                    self.logger.error(f"Error finding path with all info: {response_message.error_message}")
                    return None
            else:
                self.logger.warning(f"No response received for find_path_with_all_info (timeout: {timeout}s)")
                return None

        except Exception as e:
            self.logger.error(f"Error finding path with all info: {str(e)}")
            return None
