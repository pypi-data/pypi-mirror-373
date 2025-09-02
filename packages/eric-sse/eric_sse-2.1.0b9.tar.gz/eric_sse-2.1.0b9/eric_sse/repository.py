from typing import Iterable
from abc import ABC, abstractmethod

from eric_sse.connection import Connection
from eric_sse.entities import AbstractChannel
from eric_sse.interfaces import ChannelRepositoryInterface, ConnectionRepositoryInterface, ListenerRepositoryInterface, \
    QueueRepositoryInterface
from eric_sse.prefabs import SSEChannel
from eric_sse.exception import RepositoryError

class KvStorage(ABC):
    @abstractmethod
    def fetch_by_prefix(self, prefix: str) -> Iterable[any]:
        pass

    @abstractmethod
    def fetch_all(self) -> Iterable[any]:
        pass

    @abstractmethod
    def upsert(self, key: str, value: any):
        pass

    @abstractmethod
    def fetch_one(self, key: str) -> any:
        pass

    @abstractmethod
    def delete(self, key: str):
        pass


class InMemoryStorage(KvStorage):

    #TODO raise RepositoryError and test

    def __init__(self, objects: dict[str, any] = None):
        self.objects = objects or {}

    objects: dict[str, any] = {}

    def fetch_by_prefix(self, prefix: str) -> Iterable[any]:
        for k, obj in self.objects.items():
            if k.startswith(prefix):
                yield obj

    def fetch_all(self) -> Iterable[any]:
        for obj in self.objects.values():
            yield obj

    def upsert(self, key: str, value: any):
        self.objects[key] = value

    def fetch_one(self, key: str) -> any:
        try:
            return self.objects[key]
        except KeyError:
            raise RepositoryError(f'Item not found {key}') from None

    def delete(self, key: str):
        del self.objects[key]

class AbstractChannelRepository(ChannelRepositoryInterface, ABC):
    def __init__(self, storage: KvStorage, connections_repository: ConnectionRepositoryInterface):
        self.__storage = storage
        self.__connections_repository = connections_repository

    @property
    def connections_repository(self) -> ConnectionRepositoryInterface:
        return self.__connections_repository

    @abstractmethod
    def _create_channel(self, channel_data: dict) -> any:
        pass

    @staticmethod
    @abstractmethod
    def _channel_to_dict(channel: AbstractChannel) -> dict:
        pass

    def _setup_channel(self, channel: AbstractChannel):
        for connection in self.__connections_repository.load_all(channel_id=channel.id):
            channel.register_connection(connection)
        return channel

    def load_all(self) -> Iterable[any]:
        for channel_data in self.__storage.fetch_all():
            yield self._create_channel(channel_data)

    def load_one(self, channel_id: str) -> any:
        channel = self._create_channel(self.__storage.fetch_one(channel_id))
        for connection in self.__connections_repository.load_all(channel_id=channel.id):
            channel.register_connection(connection)
        return channel

    def persist(self, channel: AbstractChannel):
        self.__storage.upsert(channel.id, self._channel_to_dict(channel))
        for connection in channel.get_connections():
            self.__connections_repository.persist(channel_id=channel.id, connection=connection)

    def delete(self, channel_id: str):
        channel = self.load_one(channel_id)
        for connection in self.__connections_repository.load_all(channel_id=channel.id):
            self.__connections_repository.delete(channel_id=channel_id, connection_id=connection.id)
        self.__storage.delete(channel_id)



class AbstractConnectionRepository(ConnectionRepositoryInterface):

    def __init__(
            self,
            storage: KvStorage,
            listeners_repository: ListenerRepositoryInterface,
            queues_repository: QueueRepositoryInterface
    ):
        self.__storage = storage
        self.__listeners_repository = listeners_repository
        self.__queues_repository = queues_repository

    @property
    def queues_repository(self) -> QueueRepositoryInterface:
        return self.__queues_repository

    @property
    def listeners_repository(self) -> ListenerRepositoryInterface:
        return self.__listeners_repository

    def _create_connection(self, connection_id: str) -> any:
        listener = self.__listeners_repository.load(connection_id=connection_id)
        queue = self.__queues_repository.load(connection_id=connection_id)

        return Connection(listener=listener, queue=queue, connection_id=connection_id)

    @abstractmethod
    def _create_listener(self, listener_data: dict) -> any:
        pass

    @abstractmethod
    def _create_queue(self, queue_data: dict) -> any:
        pass

    def load_all(self, channel_id: str) -> Iterable[Connection]:
        for connection_data in self.__storage.fetch_by_prefix(f'{channel_id}:'):
            yield self._create_connection(connection_data['id'])


    def load_one(self, channel_id: str, connection_id: str) -> Connection:
        return self._create_connection(self.__storage.fetch_one(f'{channel_id}:{connection_id}'))

    def persist(self, channel_id: str, connection: Connection):
        self.__listeners_repository.persist(connection_id=connection.id, listener=connection.listener)
        self.__queues_repository.persist(connection_id=connection.id, queue=connection.queue)
        self.__storage.upsert(f'{channel_id}:{connection.id}', {'id': connection.id})

    def delete(self, channel_id: str, connection_id: str):
        self.__listeners_repository.delete(connection_id=connection_id)
        self.__queues_repository.delete(connection_id=connection_id)
        self.__storage.delete(key=f'{channel_id}:{connection_id}')

class SSEChannelRepository(AbstractChannelRepository):

    def _create_channel(self, channel_data: dict) -> SSEChannel:
        return SSEChannel(**channel_data)

    @staticmethod
    def _channel_to_dict(channel: SSEChannel) -> dict:
        return {
            'retry_timeout_milliseconds': channel.retry_timeout_milliseconds,
            'stream_delay_seconds': channel.stream_delay_seconds,
            'channel_id': channel.id,
        }