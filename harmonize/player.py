from __future__ import annotations

import asyncio
from asyncio import Event
from time import time
from typing import Optional, TYPE_CHECKING, overload

from async_timeout import timeout as _timeout
from disnake import VoiceProtocol, Client, VoiceState
from loguru import logger

from harmonize.abstract import Filter
from harmonize.connection import Pool
from harmonize.enums import EndReason, LoopStatus
from harmonize.exceptions import RequestError, InvalidChannelStateException
from harmonize.objects import Track, MISSING
from harmonize.queue import Queue

if TYPE_CHECKING:
    from harmonize.connection import Node
    from disnake.channel import VocalGuildChannel
    from disnake import Guild

__all__ = (
    "Player",
    "Queue"
)


class Player(VoiceProtocol):
    channel: VocalGuildChannel

    def __call__(self, client: Client, channel: VocalGuildChannel) -> Player:
        """
        Calls the Player instance, initializing it with a client and a channel.

        Args:
            client (Client): The client instance to initialize the player with.
            channel (VocalGuildChannel): The channel to initialize the player with.

        Returns:
            Player: The initialized Player instance.
        """
        super().__init__(client, channel)
        return self

    def __init__(self, *args, **kwargs) -> None:
        """
        Initializes a Player instance.

        Initializes a Player instance with the given arguments and keyword arguments.
        Sets up the internal state of the player, including the node, connection.rst event,
        voice state, user data, volume, and current track. Also sets up the queue,
        history, and filters.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        """
        self._node: Node = Pool.get_best_node()
        self._connection_event: Event = asyncio.Event()
        self._connected: bool = False
        self._voice_state: dict[str, any] = {}
        self._user_data: dict[any, any] = {}
        self._volume: int = 100
        self._paused: bool = False

        self.guild: Optional[Guild] = None
        self.loop: LoopStatus = LoopStatus(0)
        self.position_timestamp: int = 0
        self.last_position: int = 0
        self.last_update: int = 0

        self._queue: Queue = Queue(self)
        self._filters: dict[str, Filter] = {}

        super().__init__(*args, **kwargs)

    @property
    def node(self) -> Node:
        """
        Gets the current node instance associated with the player.

        Returns:
            Node: The current node instance associated with the player.
        """
        return self._node

    @property
    def is_playing(self) -> bool:
        """
        Checks if the player is currently playing a track.

        Returns:
            bool: True if the player is playing a track, False otherwise.
        """
        return self.queue.current is not None and not self._paused and self._connected

    @property
    def connected(self) -> bool:
        """
        Gets whether the player is currently connected to a voice channel.

        Returns:
            bool: Whether the player is currently connected to a voice channel.
        """
        return self._connected

    @property
    def paused(self) -> bool:
        """
        Gets whether the player is currently paused.

        Returns:
            bool: Whether the player is currently paused.
        """
        return self._paused

    @property
    def user_data(self) -> dict[any, any]:
        """
        Gets the user data associated with the player.

        Returns:
            dict[any, any]: A copy of the user data dictionary.
        """
        return self._user_data.copy()

    @property
    def volume(self) -> int:
        """
        Gets the current volume of the player.

        Returns:
            int: The current volume of the player.
        """
        return self._volume

    @property
    def queue(self) -> Queue:
        """
        Returns a copy of the queue of tracks.

        Returns:
            list[Track]: A copy of the list of tracks in the queue.
        """
        return self._queue

    @property
    def filters(self) -> list[Filter]:
        """
        Gets the list of filters applied to the player.

        Returns:
            list[Filter]: A list of filters applied to the player.
        """
        return list(self._filters.values())

    async def on_voice_server_update(self, data: dict) -> None:
        self._voice_state.update(endpoint=data['endpoint'], token=data['token'])

        if 'sessionId' not in self._voice_state:
            logger.warning(f'Player ({self.guild.id}) Missing sessionId, is the client User ID correct?')

        await self._dispatch_voice_update()

    async def on_voice_state_update(self, data: dict) -> None:
        if not data['channel_id']:
            return await self.disconnect(force=True)

        if data['session_id'] != self._voice_state.get('sessionId'):
            self._voice_state.update(sessionId=data['session_id'])

            await self._dispatch_voice_update()

    async def _dispatch_voice_update(self) -> None:
        if {'sessionId', 'endpoint', 'token'} == self._voice_state.keys():
            await self._node.update_player(guild_id=self.guild.id, voice_state=self._voice_state)
            self._connection_event.set()

    async def handle_event(self, reason: EndReason) -> None:
        """
        Handles an event triggered by the player, such as a track finishing or a load failure.

        Parameters:
            reason (EndReason): The reason for the event.

        Returns:
            None
        """
        if (
                reason.value == EndReason.FINISHED.value
                or reason.value == EndReason.LOAD_FAILED.value
        ):
            try:
                await self.play()
            except RequestError as error:
                logger.error(
                    'Encountered a request error whilst '
                    f'starting a new track on guild ({self.guild.id})'
                )

    async def update_state(self, state: dict) -> None:
        """
        Updates the state of the player with the given state dictionary.

        Parameters:
            state (dict): The state dictionary containing the 'position' and 'time' keys.

        Returns:
            None
        """
        self.last_update = int(time() * 1000)
        self.last_position = state.get('position', 0)
        self.position_timestamp = state.get('time', 0)

    def dispatch(self, name: str, *args) -> None:
        """
        Dispatches a message to the client with the given name and arguments.

        Parameters:
            name (str): The name of the message to dispatch.
            *args: Variable number of arguments.

        Returns:
            None
        """
        self._node.client.dispatch(f"harmonize_{name}", *args)

    def add_user_data(self, **kwargs: any) -> None:
        """
        Adds the given keyword arguments to the user data dictionary.

        Parameters:
            **kwargs (any): The keyword arguments to be added to the user data dictionary.

        Returns:
            None
        """
        self._user_data.update(kwargs)

    def fetch_user_data(self, key: any) -> any:
        """
        Retrieves the value associated with the specified key from the user data dictionary.

        Parameters:
            key (any): The key to retrieve the value from the user data dictionary.

        Returns:
            any: The value associated with the specified key, or None if the key is not found.
        """
        return self._user_data.get(key)

    async def _play_back(
            self,
            track: Track = MISSING,
            start_time: int = MISSING,
            end_time: int = MISSING,
            no_replace: bool = MISSING,
            volume: int = MISSING,
            pause: bool = MISSING,
            **options
    ) -> Optional[dict[str, any]]:
        if start_time is not MISSING:
            if not isinstance(start_time, int) or 0 > start_time:
                raise ValueError('Start_time must be an int with a value equal to, or greater than 0')

            options['position'] = start_time

        if end_time is not MISSING:
            if not isinstance(end_time, int) or 1 > end_time:
                raise ValueError('End_time must be an int with a value equal to, or greater than 1')

            options['end_time'] = end_time

        if no_replace is not MISSING:
            if not isinstance(no_replace, bool):
                raise TypeError('No_replace must be a bool')

            options['no_replace'] = no_replace

        if volume is not MISSING:
            if not isinstance(volume, int):
                raise TypeError('Volume must be an int')

            self._volume = max(min(volume, 1000), 0)
            options['volume'] = self._volume

        if pause is not MISSING:
            if not isinstance(pause, bool):
                raise TypeError('Pause must be a bool')

            options['paused'] = pause

        track = await self._queue._go_to_next(track)
        return await self._node.update_player(
            guild_id=self.guild.id,
            encoded_track=track.encoded,
            **options
        )

    async def play(
            self,
            track: Optional[Track] = MISSING,
            start_time: int = MISSING,
            end_time: int = MISSING,
            no_replace: bool = MISSING,
            volume: int = MISSING,
            pause: bool = MISSING,
            **kwargs
    ) -> None:
        """
        Plays a track with the given parameters.

        Parameters
        ----------
        track : Optional[Track]
            The track to play. If MISSING, the next track in the queue will be played.
        start_time : int
            The start time of the track. If MISSING, the track will start from the beginning.
        end_time : int
            The end time of the track. If MISSING, the track will play until its end.
        no_replace : bool
            Whether to replace the current track or not. If True, the current track will not be replaced.
        volume : int
            The volume of the track. If MISSING, the current volume will be used.
        pause : bool
            Whether to pause the track after playing. If MISSING, the track will not be paused.

        Returns
        -------
        None
        """
        if no_replace is True and self.queue.current:
            return

        self.last_position = 0
        self.position_timestamp = 0

        if pause is not MISSING and isinstance(pause, bool):
            self._paused = pause

        if start_time is not MISSING:
            if not isinstance(start_time, int) or not 0 <= start_time < track.duration:
                raise ValueError(
                    'start_time must be an int with a value equal to, or greater than 0, '
                    'and less than the track duration'
                )

            self.last_position = start_time

        if end_time is not MISSING:
            if not isinstance(end_time, int) or not 1 <= end_time <= track.duration:
                raise ValueError(
                    'end_time must be an int with a value equal to, or greater than 1, '
                    'and less than, or equal to the track duration'
                )

        response = await self._play_back(
            track,
            start_time,
            end_time,
            no_replace,
            volume,
            pause,
            **kwargs
        )

        if response is not None:
            self._paused = response['paused']

    async def stop(self) -> None:
        """
        Stops the current player.

        This function updates the player state by setting the encoded track to None and
        resets the current track.

        Returns
        -------
        None
        """
        await self._node.update_player(guild_id=self.guild.id, encoded_track=None)
        self.queue._current = None

    async def skip(self) -> Optional[Track]:
        """
        Skips the current track in the player's queue.

        This function does not take any parameters. It returns the track that was skipped.
        """
        old = self.queue.current
        await self.play()
        return old

    async def set_pause(self, paused: bool) -> None:
        """
        Sets the pause state of the player.

        Parameters
        ----------
        paused : bool
            Whether the player should be paused or not.

        Returns
        -------
        None
        """
        await self._node.update_player(guild_id=self.guild.id, paused=paused)
        self._paused = paused

    async def change_volume(self, volume: int) -> None:
        """
        Changes the volume of the player.

        Parameters
        ----------
        volume : int
            The new volume of the player. It will be clamped between 0 and 1000.

        Returns
        -------
        None
        """
        volume = max(min(volume, 1000), 0)
        await self._node.update_player(guild_id=self.guild.id, volume=volume)
        self._volume = volume

    async def seek(self, position: int) -> None:
        """
        Seeks to a specific position in the player.

        Parameters
        ----------
        position : int
            The position to seek to.

        Returns
        -------
        None
        """
        await self._node.update_player(guild_id=self.guild.id, position=position)

    async def remove_filters(self) -> None:
        """
        Removes all audio filters from the player.

        Returns
        -------
        None
        """
        self._filters.clear()
        await self._node.update_player(
            guild_id=self.guild.id,
            filters=list(self._filters.values())
        )

    @overload
    async def update_filters(self, filter: Filter) -> None:
        ...

    @overload
    async def update_filters(self, filters: list[Filter]) -> None:
        ...

    async def update_filters(self, **kwargs) -> None:
        """
        Updates the player's audio filters.

        Parameters
        ----------
        **kwargs
            Keyword arguments containing the filters to update.
            - filters (list[Filter]): The list of filters to update.
            - filter (Filter): The filter to update.

        Returns
        -------
        None
        """
        filters = self._get_filters_from_kwargs(kwargs)
        serialized_filters: dict[str, Filter] = self._filters.copy()

        for i in filters:
            self._is_filter(i)
            serialized_filters[type(i).__name__.lower()].update(**i.values)

        self._filters = serialized_filters
        await self._node.update_player(
            guild_id=self.guild.id,
            filters=list(self._filters.values())
        )

    @overload
    async def set_filters(self, filter: Filter) -> None:
        ...

    @overload
    async def set_filters(self, filters: list[Filter]) -> None:
        ...

    async def set_filters(self, **kwargs) -> None:
        """
        Sets the player's audio filters.

        Parameters
        ----------
        **kwargs
            Keyword arguments containing the filters to set.
            - filters (list[Filter]): The list of filters to set.
            - filter (Filter): The filter to set.

        Returns
        -------
        None
        """
        filters = self._get_filters_from_kwargs(kwargs)

        serialized_filters: dict[str, Filter] = {}
        for i in filters:
            self._is_filter(i)
            serialized_filters[type(i).__name__.lower()] = i

        self._filters = serialized_filters
        await self._node.update_player(
            guild_id=self.guild.id,
            filters=list(self._filters.values())
        )

    @classmethod
    def _get_filters_from_kwargs(cls, kwargs: dict[any, any], /) -> list[Filter]:
        filters = []
        if 'filters' in kwargs:
            filters = kwargs.pop('filters')
        elif 'filter' in kwargs:
            filters = [kwargs.pop('filter')]

        if not filters:
            raise ValueError('At least one filter must be specified')

        return filters

    @classmethod
    def _is_filter(cls, _filter: any, /) -> None:
        if not issubclass(_filter.__class__, Filter):
            raise TypeError(f'Expected subclass of type Filter, not {_filter.__name__}')

        if not isinstance(_filter, Filter):
            raise ValueError('Filter must be an instance of Filter')

    @classmethod
    async def connect_to_channel(cls, channel: VocalGuildChannel, /, **kwargs) -> Player:
        """
        Connects a player to a specified channel.

        Parameters:
            channel (VocalGuildChannel): The channel to connect the player to.
            **kwargs: Additional keyword arguments to be passed to the player.

        Returns:
            Player: The connected player.

        Raises:
            None
        """
        player = await channel.connect(cls=cls)  # type: ignore
        player.add_user_data(**kwargs)

        return player

    async def connect(
            self, *,
            timeout: float = 10.0,
            reconnect: bool,
            self_deaf: bool = True,
            self_mute: bool = False
    ) -> None:
        """
        Connects the player to a voice channel.

        Parameters:
            timeout (float): The timeout in seconds before the connection.rst attempt is cancelled. Defaults to 10.0.
            reconnect (bool): Whether the player should reconnect if the connection.rst is lost.
            self_deaf (bool): Whether the player should be deafened in the voice channel. Defaults to True.
            self_mute (bool): Whether the player should be muted in the voice channel. Defaults to False.

        Returns:
            None
        """
        if self.channel is MISSING:
            raise InvalidChannelStateException(
                f"Player tried to connect without a valid channel: " +
                'Please use "disnake.VoiceChannel.connect(cls=...)" and pass this Player to cls.'
            )

        if not self.guild:
            self.guild = self.channel.guild

        assert self.guild is not None
        await self.guild.change_voice_state(channel=self.channel, self_mute=self_mute, self_deaf=self_deaf)

        try:
            async with _timeout(timeout):
                await self._connection_event.wait()
        except (asyncio.TimeoutError, asyncio.CancelledError):
            logger.warning("Can't connect to channel. Destroying...")
            return
        else:
            self._connected = True
            self._node.players[self.guild.id] = self

    async def _destroy(self) -> None:
        self._connection_event.clear()
        self._connected = False

        await self.guild.change_voice_state(channel=None)

        try:
            self.cleanup()
        except (AttributeError, KeyError):
            pass

        del self._node.players[self.guild.id]
        await self._node.destroy_player(self.guild.id)

    async def disconnect(self, **kwargs: any) -> None:
        """
        Disconnects the player from the voice channel.

        This method asynchronously calls the `_destroy` method to disconnect the player from the voice channel.
        After the disconnection is complete, it dispatches a "player_disconnected" event with the player as the payload.

        Parameters:
            **kwargs (Any): Additional keyword arguments.

        Returns:
            None
        """
        await self._destroy()
        self.dispatch("player_disconnect", self)

    async def move_to(
            self,
            channel: VocalGuildChannel | None,
            *,
            timeout: float = 10.0,
            self_deaf: Optional[bool] = True,
            self_mute: Optional[bool] = None,
    ) -> None:
        """
        Asynchronously moves the player to a specified voice channel.

        Args:
            channel (VocalGuildChannel | None): The voice channel to move the player to. If `None`, the player will remain in its current channel.
            timeout (float, optional): The maximum time in seconds to wait for the player to connect to the channel. Defaults to 10.0.
            self_deaf (Optional[bool], optional): Whether the player should be deafened in the voice channel. If `None`, the player's deafened status will be inherited from the current voice state. Defaults to `True`.
            self_mute (Optional[bool], optional): Whether the player should be muted in the voice channel. If `None`, the player's muted status will be inherited from the current voice state. Defaults to `None`.

        Returns:
            None

        Raises:
            InvalidChannelStateException: If the player tries to move without a valid guild or channel.

        Notes:
            This method will clear the `_connection_event` event and wait for the player to connect to the specified channel. If the connection.rst attempt times out or is cancelled, the player will be destroyed.

        """
        if not self.guild:
            raise InvalidChannelStateException("Player tried to move without a valid guild.")

        if not channel:
            raise InvalidChannelStateException("Player tried to move without a valid channel.")

        self._connection_event.clear()
        voice: VoiceState | None = self.guild.me.voice

        if self_deaf is None and voice:
            self_deaf = voice.self_deaf

        if self_mute is None and voice:
            self_mute = voice.self_mute

        self_deaf = bool(self_deaf)
        self_mute = bool(self_mute)

        await self.guild.change_voice_state(channel=channel, self_mute=self_mute, self_deaf=self_deaf)

        try:
            async with _timeout(timeout):
                await self._connection_event.wait()
        except (asyncio.TimeoutError, asyncio.CancelledError):
            logger.warning("Can't connect to channel. Destroying...")
            await self._destroy()
