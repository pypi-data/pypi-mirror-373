import asyncio
import logging

from rosy.asyncio import LockableWriter, Reader, Writer
from rosy.node.codec import NodeMessageCodec
from rosy.node.service.requesthandler import ServiceRequestHandler
from rosy.node.service.types import ServiceRequest
from rosy.node.topic.messagehandler import TopicMessageHandler
from rosy.node.topic.types import TopicMessage

logger = logging.getLogger(__name__)


class ClientHandler:
    def __init__(
        self,
        node_message_codec: NodeMessageCodec,
        topic_message_handler: TopicMessageHandler,
        service_request_handler: ServiceRequestHandler,
    ):
        self.node_message_codec = node_message_codec
        self.topic_message_handler = topic_message_handler
        self.service_request_handler = service_request_handler

    async def handle_client(self, reader: Reader, writer: Writer) -> None:
        peer_name = writer.get_extra_info("peername") or writer.get_extra_info(
            "sockname"
        )
        logger.debug(f"New connection from: {peer_name}")

        writer = LockableWriter(writer)

        while True:
            try:
                obj = await self.node_message_codec.decode_topic_message_or_service_request(
                    reader
                )
            except EOFError:
                logger.debug(f"Closed connection from: {peer_name}")
                return

            if isinstance(obj, TopicMessage):
                await self.topic_message_handler.handle_message(obj)
            elif isinstance(obj, ServiceRequest):
                asyncio.create_task(
                    self.service_request_handler.handle_request(obj, writer),
                    name=f"Handle service request {obj.id} from {peer_name}",
                )
            else:
                raise RuntimeError("Unreachable code")
