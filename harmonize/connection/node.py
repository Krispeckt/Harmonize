from __future__ import annotations

from asyncio import get_event_loop
from collections import defaultdict
from typing import Optional, Union, TypeVar, TYPE_CHECKING
from urllib import parse

from disnake import Client

from harmonize.abstract import Serializable, Filter
from harmonize.connection.cache import LFUCache
from harmonize.connection.transport import Transport
from harmonize.enums import NodeStatus, CacheCapacity
from harmonize.exceptions import InvalidSession, RequestError
from harmonize.objects import Track, LoadResult, MISSING, Stats

if TYPE_CHECKING:
    from harmonize.player import Player

T = TypeVar('T')

__all__ = (
    "Node",
)


class Node:
    """Represents a lavalink node

    Operations
    ----------
        .. describe:: x == y

            Checks if two nodes are the same.

        .. describe:: x != y

            Checks if two nodes are not the same.

        .. describe:: hash(x)

            Return the node's hash.

    Attributes
    ----------
        identifier : str
            A unique identifier for the node.

        host : str
            The host address of the node.

        port : int
            The port number of the node.

        ssl : bool
            A boolean indicating whether the node uses SSL.

        client : :class:`disnake.Client`
            The client instance associated with the node.

        cache_capacity : :class:`harmonize.enums.CacheCapacity`
            The capacity of the node's cache. Defaults to CacheCapacity.LITTLE.

        retries : int
            The number of retries for the node's transport. Defaults to 10.

        heartbeat : float
            The heartbeat interval for the node's transport. Defaults to 15.0.

        status : :class:`harmonize.enums.NodeStatus`
            The current status of the node. Defaults to NodeStatus.DISCONNECTED

        stats : :class:`harmonize.objects.Stats`
            Node statistics object associated with the node
    """
    __cache: Optional[LFUCache] = None

    @classmethod
    def _load_cache(cls, capacity: int) -> None:
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
    ) -> None:
        self.port = port
        self.host = host

        self._identifier = identifier
        self._uri = f"http{'s' if ssl else ''}://{host}:{port}/"
        self._password = password
        self._heartbeat: float = heartbeat
        self._client: Client = client

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
        return self._identifier

    @property
    def client(self) -> Client:
        return self._client

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def http_uri(self) -> str:
        return self._uri

    @property
    def status(self) -> NodeStatus:
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
        return hash(self._identifier + self.http_uri)

    def __eq__(self, other: any) -> bool:
        if not isinstance(other, Node):
            raise ValueError("Nodes can only be compared with other Nodes")

        return all([
            other._identifier == self._identifier,
            other.http_uri == self.http_uri
        ])

    def __ne__(self, other: any) -> bool:
        return not self.__eq__(other)

    def connect(self, force: bool = False) -> None:
        """
        Connects the node's transport.

        Parameters
        ----------
            force : bool
                Whether to force a reconnection. Defaults to False.

        Returns
        -------
            None

        Raises
        ------
            AuthorizationError
                Throws when authorization fails

            NodeUnknownError
                Thrown at 404 status
        """
        if self._transport.is_alive:
            if not force:
                return

            self._transport.close()

        get_event_loop().create_task(self._transport.connect())

    def close(self) -> None:
        """
        Closes the node's transport connection.

        Returns
        -------
            None
        """
        self._client.loop.create_task(self._transport.close())

    async def destroy_player(self, guild_id: str | int) -> bool:
        """|coro|

        Destroys a player with the given guild ID.

        Args
        ----
            guild_id : str | int
                The ID of the guild to destroy the player for.

        Returns
        -------
            bool
                Whether the player was successfully destroyed.

        Raises
        ------
            InvalidSession
                Throws if player can't be destroyed because of invalid session

            Forbidden
                If the request is forbidden.

            RequestError
                Throws an error when the request fails.

            IOError
                If the connection has been closed
        """
        if not self.session_id:
            raise InvalidSession('Cannot destroy a player without a valid session ID!')

        return await self.request('DELETE', f'sessions/{self.session_id}/players/{guild_id}')

    async def get_routeplanner_status(self) -> dict[str, any]:
        """|coro|

        Retrieves the current status of the route planner.

        Returns
        -------
            dict[str, any]
                The status of the route planner.

        Raises
        ------
            Forbidden
                If the request is forbidden.

            RequestError
                Throws an error when the request fails.

            IOError
                If the connection has been closed
        """
        return await self.request('GET', 'routeplanner/status')

    async def routeplanner_free_address(self, address: str) -> bool:
        """|coro|

        Frees a route planner address.

        Parameters
        ----------
            address : str
                The address to free.

        Returns
        -------
            bool
                Whether the address was successfully freed.

        Raises
        ------
            Forbidden
                If the request is forbidden.

            IOError
                If the connection has been closed
        """
        try:
            return await self.request('POST', 'routeplanner/free/address', params={'address': address})  # type: ignore
        except RequestError:
            return False

    async def routeplanner_free_all_failing(self) -> bool:
        """|coro|

        Frees all failing route planner addresses.

        Returns
        -------
            bool
                Whether all addresses were successfully freed.

        Raises
        ------
            Forbidden
                If the request is forbidden.

            IOError
                If the connection has been closed
        """
        try:
            return await self.request('POST', 'routeplanner/free/all')  # type: ignore
        except RequestError:
            return False

    async def get_tracks(self, query: str) -> LoadResult:
        """|coro|

        Retrieves tracks based on the provided query.

        Parameters
        ----------
            query : str
                The query string to search for tracks.

        Returns
        -------
            :class:`harmonize.objects.LoadResult`
                The result of the load tracks request.

        Raises
        ------
            Forbidden
                If the request is forbidden.

            RequestError
                Throws an error when the request fails.

            IOError
                If the connection has been closed
        """
        encoded_query: str = parse.quote(query)
        if potential := self.__cache.get(encoded_query, None):
            return potential

        data = await self.request('GET', 'loadtracks', params={'identifier': query}, to=LoadResult)
        if not data.error:
            self.__cache.put(encoded_query, data)

        return data

    async def decode_tracks(self, tracks: list[str]) -> list[Track]:
        """|coro|

        Decodes a list of tracks.

        Parameters
        ----------
            tracks : list[str]
                A list of track IDs to decode.

        Returns
        -------
            list[:class:`harmonize.objects.Track`]
                A list of decoded Track objects.

        Raises
        ------
            Forbidden
                If the request is forbidden.

            RequestError
                Throws an error when the request fails.

            IOError
                If the connection has been closed
        """
        response = await self.request('POST', 'decodetracks', json={'tracks': tracks})
        return list(map(Track.from_dict, response))

    async def decode_track(self, track: str) -> Track:
        """|coro|

        Decodes a single track.

        Parameters
        ----------
            track : str
                The track ID to decode.

        Returns
        -------
            :class:`harmonize.objects.Track`
                The decoded Track object.

        Raises
        ------
            Forbidden
                If the request is forbidden.

            RequestError
                Throws an error when the request fails.

            IOError
                If the connection has been closed
        """
        encoded_query: str = parse.quote(track)
        if potential := self.__cache.get(encoded_query, None):
            return potential

        if data := await self.request('GET', 'decodetrack', params={'track': track}, to=Track):
            self.__cache.put(encoded_query, data)

        return data

    async def get_info(self) -> dict[str, any]:
        """|coro|

        Retrieves information about the node.

        Returns:
            dict[str, any]
                A dictionary containing information about the node.

        Raises
        ------
            Forbidden
                If the request is forbidden.

            RequestError
                Throws an error when the request fails.

            IOError
                If the connection has been closed
        """
        return await self.request('GET', 'info')

    async def get_stats(self) -> dict[str, any]:
        """|coro|

        Retrieves statistics about the node.

        Returns
        -------
            dict[str, any]
                A dictionary containing statistics about the node.

        Raises
        ------
            Forbidden
                If the request is forbidden.

            RequestError
                Throws an error when the request fails.

            IOError
                If the connection has been closed
        """
        return await self.request('GET', 'stats')

    async def get_player(self, guild_id: Union[str, int]) -> dict[str, any]:
        """|coro|

        Retrieves a player with the given guild ID.

        Parameters
        ----------
            guild_id: str | int
                The ID of the guild to retrieve the player for.

        Returns
        -------
            dict[str, any]
                A dictionary containing information about the player.

        Raises
        ------
            InvalidSession
                Throws if player can't be retrieved because of invalid session.

            Forbidden
                If the request is forbidden.

            RequestError
                Throws an error when the request fails.

            IOError
                If the connection has been closed
        """
        if not self.session_id:
            raise InvalidSession('Cannot retrieve a player without a valid session ID!')

        return await self.request('GET', f'sessions/{self.session_id}/players/{guild_id}')  # type: ignore

    async def get_players(self) -> list[dict[str, any]]:
        """|coro|

        Retrieves a list of players associated with the session ID.

        Returns
        -------
            list[dict[str, any]]
                A list of dictionaries containing information about the players.

        Raises
        ------
            InvalidSession
                Throws if player can't be retrieved because of invalid session.

            Forbidden
                If the request is forbidden.

            RequestError
                Throws an error when the request fails.

            IOError
                If the connection has been closed
        """
        if not self.session_id:
            raise InvalidSession('Cannot retrieve a list of players without a valid session ID!')

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
        """|coro|

        Updates the state of a player with the given guild ID.

        Parameters
        ----------
        guild_id : Union[str, int]
            The ID of the guild to update the player for.
        encoded_track : Optional[str] = MISSING
            The encoded track to update the player with.
            If both this and `identifier` are specified, an error will be raised.
        identifier : str = MISSING
            The identifier of the track to update the player with.
            If both this and `encoded_track` are specified, an error will be raised.
        no_replace : bool = MISSING
            Whether to replace the current track with the new one. Defaults to False.
        position : int = MISSING
            The position of the track to update the player with. If not specified, the current position will be used.
        end_time : int = MISSING
            The end time of the track to update the player with. If not specified, the current end time will be used.
        volume : int = MISSING
            The volume of the track to update the player with. If not specified, the current volume will be used.
        paused : bool = MISSING
            Whether the track is paused. If not specified, the current paused state will be used.
        filters : Optional[list[Filter]] = MISSING
            A list of filters to apply to the track. If not specified, no filters will be applied.
        voice_state : dict[str, any] = MISSING
            The voice state of the player. If not specified, the current voice state will be used.
        user_data : dict[str, any] = MISSING
            Additional user data to associate with the player.
            If not specified, no additional user data will be associated.
        **kwargs
            Additional keyword arguments to pass to the request.

        Returns
        -------
        Optional[dict[str, any]]
            The updated player information, or None if no update was made.

        Raises
        ------
            InvalidSession
                Throws if player can't be retrieved because of invalid session.

            ValueError
                If both `encoded_track` and `identifier` are specified, or if the specified parameters are invalid.

            Forbidden
                If the request is forbidden.

            RequestError
                Throws an error when the request fails.

            IOError
                If the connection has been closed
            """
        session_id = self.session_id

        if not session_id:
            raise InvalidSession('Cannot update the state of a player without a valid session ID!')

        if encoded_track is not MISSING and identifier is not MISSING:
            raise ValueError(
                'encoded_track and identifier are mutually exclusive options, you may not specify both together.'
            )

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
            self,
            session_id: int,
            resuming: bool = None,
            timeout: int = None
    ) -> Optional[dict[str, any]]:
        """|coro|

        Updates the state of a session with the given session ID.

        Parameters
        ----------
        session_id : int
            The ID of the session to update.
        resuming : bool = None
            Whether the session should resume playback. Defaults to None.
        timeout : int = None
            The timeout for the session, in seconds. Defaults to None.

        Returns
        -------
        Optional[dict[str, any]]
            The updated session information, or None if no update was made.

        Raises
        ------
            ValueError
                If the specified parameters are invalid.

            Forbidden
                If the request is forbidden.

            RequestError
                Throws an error when the request fails.

            IOError
                If the connection has been closed
        """
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
            self,
            method: str,
            path: str,
            *,
            to: Optional[Serializable] = None,
            trace: bool = False,
            **kwargs
    ) -> Union[T, str, bool, dict[any, any], list[any]]:
        """|coro|

        Sends an HTTP request to the specified path on the node's transport.

        Parameters
        ----------
        method : str
            The HTTP method to use for the request, e.g. 'GET', 'POST', 'PUT', 'DELETE'.
        path : str
            The path of the resource to request, relative to the base URL of the node.
        to : :class:`harmonize.abstract.Serializable` = None
            The class of the object to deserialize the response into
        trace : bool = False
            Whether to enable tracing for the request. Defaults to False.
        **kwargs : dict
            Additional keyword arguments to pass to the request.

        Returns
        -------
        Union[T, str, bool, dict[any, any], list[any]]
            The response from the request, deserialized into the specified type or class if provided.

        Raises
        ------
            Forbidden
                If the request is forbidden.

            RequestError
                Throws an error when the request fails.

            IOError
                If the connection has been closed
        """
        return await self._transport.request(
            method=method,
            path=path,
            to=to,
            trace=trace,
            **kwargs
        )
