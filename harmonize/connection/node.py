from __future__ import annotations

from asyncio import get_event_loop
from collections import defaultdict
from typing import Optional, Union, Type, TypeVar, TYPE_CHECKING
from urllib import parse

from disnake import Client

from harmonize.abstract.filter import Filter
from harmonize.connection.cache import LFUCache
from harmonize.enums import NodeStatus, CacheCapacity
from harmonize.exceptions import ClientError, RequestError
from harmonize.objects import Track, LoadResult, MISSING, Stats
from harmonize.connection.transport import Transport

if TYPE_CHECKING:
    from harmonize.player import Player

T = TypeVar('T')

__all__ = (
    "Node",
)


class Node:
    __cache: Optional[LFUCache] = None

    @classmethod
    def _load_cache(cls, capacity: int) -> None:
        """
        Loads the cache for the Node class.

        Args:
            capacity: The maximum number of items the cache can hold.

        Returns:
            None
        """
        if cls.__cache is None:
            cls.__cache = LFUCache(capacity=capacity)

    def __init__(
            self,
            *,
            identifier: str,
            host: str,
            port: int,
            ssl: bool,
            password: str,
            client: Client,
            cache_capacity: CacheCapacity = CacheCapacity.LITTLE,
            retries: int = 10,
            heartbeat: float = 15.0,
            resume_timeout: int = 300,
    ) -> None:
        """
        Initializes a Node instance.

        Args:
            identifier: A unique identifier for the node.
            host: The host address of the node.
            port: The port number of the node.
            ssl: A boolean indicating whether the node uses SSL.
            password: The password for the node.
            client: The client instance associated with the node.
            cache_capacity: The capacity of the node's cache. Defaults to CacheCapacity.LITTLE.
            retries: The number of retries for the node's transport. Defaults to 10.
            heartbeat: The heartbeat interval for the node's transport. Defaults to 15.0.
            resume_timeout: The resume timeout for the node's transport. Defaults to 300.

        Returns:
            None
        """
        self.port = port
        self.host = host

        self._identifier = identifier
        self._uri = f"http{'s' if ssl else ''}://{host}:{port}/"
        self._password = password
        self._heartbeat: float = heartbeat
        self._client: Client = client
        self._resume_timeout: int = resume_timeout

        self.stats = Stats.empty(self)
        self.players: dict[int, Player] = {}
        self._session_id: str | None = None
        self._status = NodeStatus.DISCONNECTED
        self._transport = Transport(
            node=self,
            ssl=ssl,
            password=password,
            heartbeat=heartbeat,
            retries=retries
        )

        self._load_cache(capacity=cache_capacity.value)

    @property
    def identifier(self) -> str:
        """
        Gets the unique identifier of the node.

        Returns:
            str: The unique identifier of the node.
        """
        return self._identifier

    @property
    def client(self) -> Client:
        """
        Gets the client instance associated with the node.

        Returns:
            Client: The client instance associated with the node.
        """
        return self._client

    @property
    def session_id(self) -> str:
        """
        Gets the current session ID of the node.

        Returns:
            str: The current session ID of the node.
        """
        return self._session_id

    @property
    def http_uri(self) -> str:
        """
        Gets the HTTP URI of the node.

        Returns:
            str: The HTTP URI of the node.
        """
        return self._uri

    @property
    def status(self) -> NodeStatus:
        """
        Gets the current status of the node.

        Returns:
            NodeStatus: The current status of the node.
        """
        return self._status

    def __repr__(self) -> str:
        return (
            f"harmonize.Node<"
            f"identifier={self._identifier}, "
            f"uri={self._uri}, "
            f"status={self._status}, "
            f"players={len(self.players)}>"
        )

    def __hash__(self) -> int:
        return hash(self._identifier)

    def __eq__(self, other: any) -> bool:
        if not isinstance(other, Node):
            raise ValueError("Nodes can only be compared with other Nodes")

        return other._identifier == self._identifier

    def connect(self, force: bool = False) -> None:
        """
        Connects the node to the transport.

        Args:
            force: Whether to force the connection.rst even if the transport is alive. Defaults to False.

        Returns:
            None
        """
        if self._transport.is_alive:
            if not force:
                return

            self._transport.close()

        get_event_loop().create_task(self._transport.connect())

    def close(self) -> None:
        """
        Closes the node's transport connection.rst.

        Returns:
            None
        """
        self._client.loop.create_task(self._transport.close())

    async def destroy_player(self, guild_id: str | int) -> bool:
        """
        Destroys a player with the given guild ID.

        Args:
            guild_id (str | int): The ID of the guild to destroy the player for.

        Returns:
            bool: Whether the player was successfully destroyed.

        Raises:
            ClientError: If the session ID is invalid.
        """
        if not self.session_id:
            raise ClientError('Cannot destroy a player without a valid session ID!')

        return await self.request('DELETE', f'sessions/{self.session_id}/players/{guild_id}')

    async def get_routeplanner_status(self) -> dict[str, any]:
        """
        Retrieves the current status of the route planner.

        Returns:
            dict[str, any]: The status of the route planner.
        """
        return await self.request('GET', 'routeplanner/status')

    async def routeplanner_free_address(self, address: str) -> bool:
        """
        Frees a route planner address.

        Args:
            address (str): The address to free.

        Returns:
            bool: Whether the address was successfully freed.
        """
        try:
            return await self.request('POST', 'routeplanner/free/address', params={'address': address})  # type: ignore
        except RequestError:
            return False

    async def routeplanner_free_all_failing(self) -> bool:
        """
        Frees all failing route planner addresses.

        Returns:
            bool: Whether all addresses were successfully freed.
        """
        try:
            return await self.request('POST', 'routeplanner/free/all')  # type: ignore
        except RequestError:
            return False

    async def get_tracks(self, query: str) -> LoadResult:
        """
        Asynchronously retrieves tracks based on the provided query.

        Args:
            query (str): The query string to search for tracks.

        Returns:
            LoadResult: The result of the load tracks request.

        Raises:
            None.
        """
        encoded_query: str = parse.quote(query)
        if potential := self.__cache.get(encoded_query, None):
            return potential

        data = await self.request('GET', 'loadtracks', params={'identifier': query}, to=LoadResult)
        if not data.error:
            self.__cache.put(encoded_query, data)

        return data

    async def decode_tracks(self, tracks: list[str]) -> list[Track]:
        """
        Asynchronously decodes a list of tracks.

        Args:
            tracks (list[str]): A list of track IDs to decode.

        Returns:
            list[Track]: A list of decoded Track objects.

        This function sends a POST request to the 'decodetracks' endpoint of the node's API with a JSON payload containing the list of track IDs. It then maps the response to a list of Track objects using the `Track.from_dict` method.

        Raises:
            RequestError: If there is an error making the request.

        """
        response = await self.request('POST', 'decodetracks', json={'tracks': tracks})
        return list(map(Track.from_dict, response))

    async def decode_track(self, track: str) -> Track:
        """
        Asynchronously decodes a single track.

        Args:
            track (str): The track ID to decode.

        Returns:
            Track: The decoded Track object.

        Raises:
            None.
        """
        encoded_query: str = parse.quote(track)
        if potential := self.__cache.get(encoded_query, None):
            return potential

        if data := await self.request('GET', 'decodetrack', params={'track': track}, to=Track):
            self.__cache.put(encoded_query, data)

        return data

    async def get_info(self) -> dict[str, any]:
        """
        Asynchronously retrieves information about the node.

        Returns:
            dict[str, any]: A dictionary containing information about the node.

        Raises:
            RequestError: If there is an error making the request.
        """
        return await self.request('GET', 'info')

    async def get_stats(self) -> dict[str, any]:
        """
        Asynchronously retrieves statistics about the node.

        Returns:
            dict[str, any]: A dictionary containing statistics about the node.
        """
        return await self.request('GET', 'stats')

    async def get_player(self, guild_id: Union[str, int]) -> dict[str, any]:
        """
        Asynchronously retrieves a player with the given guild ID.

        Args:
            guild_id (str | int): The ID of the guild to retrieve the player for.

        Returns:
            dict[str, any]: A dictionary containing information about the player.

        Raises:
            ClientError: If the session ID is invalid.
        """
        if not self.session_id:
            raise ClientError('Cannot retrieve a player without a valid session ID!')

        return await self.request('GET', f'sessions/{self.session_id}/players/{guild_id}')  # type: ignore

    async def get_players(self) -> list[dict[str, any]]:
        """
        Asynchronously retrieves a list of players associated with the session ID.

        Returns:
            list[dict[str, any]]: A list of dictionaries containing information about the players.

        Raises:
            ClientError: If the session ID is invalid.
        """
        if not self.session_id:
            raise ClientError('Cannot retrieve a list of players without a valid session ID!')

        return await self.request('GET', f'sessions/{self.session_id}/players')  # type: ignore

    async def update_player(
            self,
            guild_id: Union[str, int],
            encoded_track: Optional[str] = MISSING,
            identifier: str = MISSING,
            no_replace: bool = MISSING,
            position: int = MISSING,
            end_time: int = MISSING,
            volume: int = MISSING,
            paused: bool = MISSING,
            filters: Optional[list[Filter]] = MISSING,
            voice_state: dict[str, any] = MISSING,
            user_data: dict[str, any] = MISSING,
            **kwargs
    ) -> Optional[dict[str, any]]:
        """
        Asynchronously updates a player with the given guild ID.

        Args:
            guild_id (str | int): The ID of the guild to update the player for.
            encoded_track (str, optional): The encoded track to play. Defaults to MISSING.
            identifier (str, optional): The identifier of the track to play. Defaults to MISSING.
            no_replace (bool, optional): Whether to replace the current track. Defaults to MISSING.
            position (int, optional): The position of the track to play. Defaults to MISSING.
            end_time (int, optional): The end time of the track to play. Defaults to MISSING.
            volume (int, optional): The volume of the track to play. Defaults to MISSING.
            paused (bool, optional): Whether the track is paused. Defaults to MISSING.
            filters (list[Filter], optional): The filters to apply to the track. Defaults to MISSING.
            voice_state (dict[str, any], optional): The voice state of the player. Defaults to MISSING.
            user_data (dict[str, any], optional): The user data of the player. Defaults to MISSING.

        Returns:
            dict[str, any]: A dictionary containing information about the updated player.

        Raises:
            ClientError: If the session ID is invalid.
            ValueError: If the parameters are invalid.
        """
        session_id = self.session_id

        if not session_id:
            raise ClientError('Cannot update the state of a player without a valid session ID!')

        if encoded_track is not MISSING and identifier is not MISSING:
            raise ValueError(
                'encoded_track and identifier are mutually exclusive options, you may not specify both together.')

        params = {}
        json = kwargs.copy()

        if identifier is not MISSING or encoded_track is not MISSING:
            track = {}

            if identifier is not MISSING:
                track['identifier'] = identifier

            elif encoded_track is not MISSING:
                track['encoded'] = encoded_track

            if user_data is not MISSING:
                track['userData'] = user_data

            if no_replace is not MISSING:
                params['noReplace'] = str(no_replace).lower()

            json['track'] = track

        if position is not MISSING:
            if not isinstance(position, (int, float)):
                raise ValueError('position must be an int!')

            json['position'] = position

        if end_time is not MISSING:
            if not isinstance(end_time, int) or end_time <= 0:
                raise ValueError('end_time must be an int, and greater than 0!')

            json['endTime'] = end_time

        if volume is not MISSING:
            if not isinstance(volume, int) or not 0 <= volume <= 1000:
                raise ValueError('volume must be an int, and within the range of 0 to 1000!')

            json['volume'] = volume

        if paused is not MISSING:
            if not isinstance(paused, bool):
                raise ValueError('paused must be a bool!')

            json['paused'] = paused

        if filters is not MISSING:
            if filters is not None:
                if not isinstance(filters, list) or not all(isinstance(f, Filter) for f in filters):
                    raise ValueError('filters must be a list of Filter!')

                serialized = defaultdict(dict)

                for filter_ in filters:
                    filter_obj = serialized['pluginFilters'] if filter_.plugin_filter else serialized
                    filter_obj.update(filter_.to_dict())

                json['filters'] = serialized
            else:
                json['filters'] = {}

        if voice_state is not MISSING:
            if not isinstance(voice_state, dict):
                raise ValueError('voice_state must be a dict!')

            json['voice'] = voice_state

        if json:
            return await self.request(
                'PATCH',
                f'sessions/{session_id}/players/{guild_id}',
                params=params, json=json
            )

    async def update_session(
            self, session_id: int, resuming: bool = None, timeout: int = None
    ) -> Optional[dict[str, any]]:
        json = {}

        if resuming is not None:
            json['resuming'] = resuming

        if timeout is not None:
            if 0 >= timeout:
                raise ValueError('Timeout must be an int greater than 0!')

            json['timeout'] = timeout

        if not json:
            return None

        return await self.request('PATCH', f'sessions/{session_id}', json=json)  # type: ignore

    async def request(
            self,  # type: ignore
            method: str,
            path: str,
            *,
            to: Optional[Union[Type[T], str]] = None,
            trace: bool = False,
            **kwargs
    ) -> Union[T, str, bool, dict[any, any], list[any]]:
        """
        Makes a request to the transport.

        Args:
            method: The HTTP method of the request.
            path: The path of the request.
            to: The type to deserialize the response to. Defaults to None.
            trace: Whether to include tracing information in the request. Defaults to False.

        Returns:
            The response from the transport, deserialized to the specified type if provided.
        """
        return await self._transport.request(
            method=method,
            path=path,
            to=to,
            trace=trace,
            **kwargs
        )
