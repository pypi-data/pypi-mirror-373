import json
from typing import Dict, Any, TypeVar, Type

from h_message_bus import HaiMessage

from ....domain.messaging.request_message_topic import RequestMessageTopic

T = TypeVar('T', bound='HaiMessage')

class GraphQueryOperationResponseMessage(HaiMessage):
    """Message with results from graph query operations"""

    @classmethod
    def create(cls: Type[T], topic: str, payload: Dict[Any, Any]) -> T:
        """Create a message - inherited from HaiMessage"""
        return super().create(topic=topic, payload=payload)

    @classmethod
    def create_message(cls,
                       operation_type: str,
                       result: Dict[str, Any],
                       success: bool = True,
                       error_message: str = None) -> 'GraphQueryOperationResponseMessage':
        """
        Create a response message with graph query operation results

        Args:
            operation_type: The type of operation that was performed
            result: Dictionary containing the operation results
            success: Whether the operation was successful
            error_message: Error message if the operation failed

        Returns:
            A new GraphQueryOperationResponseMessage
        """
        payload = {
            "operation_type": operation_type,
            "result": json.dumps(result),
            "success": success
        }

        if error_message:
            payload["error_message"] = error_message

        return cls.create(
            topic=RequestMessageTopic.GRAPH_QUERY_OPERATION_RESPONSE,
            payload=payload,
        )

    @property
    def operation_type(self) -> str:
        """Get the operation type from the payload"""
        return self.payload.get("operation_type", "")

    @property
    def result(self) -> Dict[str, Any]:
        """Get the result from the payload"""
        result_str = self.payload.get("result", "{}")
        return json.loads(result_str)

    @property
    def success(self) -> bool:
        """Get the success status from the payload"""
        return self.payload.get("success", False)

    @property
    def error_message(self) -> str:
        """Get the error message from the payload"""
        return self.payload.get("error_message", "")

    @classmethod
    def from_hai_message(cls, message: HaiMessage) -> 'GraphQueryOperationResponseMessage':
        """Create a GraphQueryOperationResponseMessage from a HaiMessage"""
        payload = message.payload
        operation_type = payload.get("operation_type", "")
        result_str = payload.get("result", "{}")
        result = json.loads(result_str)
        success = payload.get("success", False)
        error_message = payload.get("error_message")

        return cls.create_message(
            operation_type=operation_type,
            result=result,
            success=success,
            error_message=error_message
        )