import logging
from asyncio import Lock, open_connection, open_unix_connection
from collections import defaultdict
from collections.abc import Iterable
from typing import NamedTuple

from rosy.asyncio import LockableWriter, Reader, Writer, close_ignoring_errors
from rosy.network import get_hostname
from rosy.socket import setup_socket
from rosy.specs import (
    ConnectionSpec,
    IpConnectionSpec,
    MeshNodeSpec,
    NodeId,
    UnixConnectionSpec,
)
from rosy.types import Host

logger = logging.getLogger(__name__)


class PeerConnection(NamedTuple):
    reader: Reader
    writer: LockableWriter

    async def close(self) -> None:
        await close_ignoring_errors(self.writer)

    def is_closing(self) -> bool:
        return self.writer.is_closing()


class PeerConnectionBuilder:
    def __init__(self, host: Host = None):
        self.host = host or get_hostname()

    async def build(
        self, conn_specs: Iterable[ConnectionSpec]
    ) -> tuple[Reader, Writer]:
        reader_writer = None
        for conn_spec in conn_specs:
            try:
                reader_writer = await self._get_connection(conn_spec)
            except (ConnectionError, IOError) as e:
                logger.error(f"Error connecting to {conn_spec}: {e!r}")
                continue

            if reader_writer is not None:
                break

        if reader_writer is None:
            raise ConnectionError("Could not connect to any connection spec")

        return reader_writer

    async def _get_connection(
        self, conn_spec: ConnectionSpec
    ) -> tuple[Reader, Writer] | None:
        if isinstance(conn_spec, IpConnectionSpec):
            reader, writer = await open_connection(
                host=conn_spec.host,
                port=conn_spec.port,
                family=conn_spec.family,
            )

            sock = writer.get_extra_info("socket")
            setup_socket(sock)

            return reader, writer
        elif isinstance(conn_spec, UnixConnectionSpec):
            if conn_spec.host != self.host:
                return None

            return await open_unix_connection(path=conn_spec.path)
        else:
            raise ValueError(f"Unrecognized connection spec: {conn_spec}")


class PeerConnectionManager:
    def __init__(self, conn_builder: PeerConnectionBuilder):
        self.conn_builder = conn_builder

        self._connections: dict[NodeId, PeerConnection] = {}
        self._connections_locks: dict[NodeId, Lock] = defaultdict(Lock)

    async def get_connection(self, node: MeshNodeSpec) -> PeerConnection:
        async with self._connections_locks[node.id]:
            connection = await self._get_cached_connection(node)
            if connection:
                return connection

            logger.debug(f"Connecting to node: {node.id}")
            reader, writer = await self.conn_builder.build(node.connection_specs)

            writer = LockableWriter(writer)

            connection = PeerConnection(reader, writer)
            self._connections[node.id] = connection
            return connection

    async def _get_cached_connection(self, node: MeshNodeSpec) -> PeerConnection | None:
        connection = self._connections.get(node.id, None)
        if not connection:
            return None

        if connection.is_closing():
            await self.close_connection(node)
            return None

        return connection

    async def close_connection(self, node: MeshNodeSpec) -> None:
        connection = self._connections.pop(node.id, None)
        if connection:
            await connection.close()
