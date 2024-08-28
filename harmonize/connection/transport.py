from __future__ import annotations

from asyncio import sleep
from typing import TYPE_CHECKING, Optional

from aiohttp import (
    ClientWebSocketResponse,
    WSServerHandshakeError,
    ClientConnectorError,
    ClientOSError,
    WSMsgType,
    WSCloseCode,
    ClientSession,
    ClientError
)
from loguru import logger

from harmonize.abstract.serializable import Serializable
from harmonize.enums import NodeStatus, EndReason, Severity
from harmonize.exceptions import AuthorizationError, NodeUnknownError, AuthenticationError
from harmonize.objects import Stats

if TYPE_CHECKING:
    from harmonize.connection.node import Node

__all__ = (
    "Transport",
)


class Transport:
    def __init__(
            self, *,
            node: Node,
            ssl: bool,
            password: str,
            heartbeat: float,
            retries: int
    ) -> None:
        self._node: Node = node

        self._port = node.port
        self._host = node.host
        self._ssl = ssl
        self._http = f"http{'s' if ssl else ''}://{self._host}:{self._port}/"
        self._password = password
        self._heartbeat = heartbeat
        self._session = ClientSession()
        self._retries = retries

        self._websocket: ClientWebSocketResponse | None = None

    @property
    def is_alive(self) -> bool:
        return self._websocket is not None and not self._websocket.closed

    @property
    def headers(self) -> dict[str, str]:
        headers = {
            "Authorization": self._password,
            "User-Id": str(self._node.client.user.id),
            "Client-Name": f"Harmonize/{self._node.client.user.name}",
        }

        if self._node.session_id is not None:
            headers['Session-Id'] = self._node.session_id

        return headers

    async def _connect_back(self) -> None:
        retries = 1
        while not self.is_alive:
            try:
                self._websocket = await self._session.ws_connect(
                    f"ws{'s' if self._ssl else ''}://{self._node.host}:{self._node.port}/v4/websocket",
                    headers=self.headers,
                    heartbeat=self._heartbeat
                )
            except Exception as e:
                if isinstance(e, WSServerHandshakeError) and e.status == 401:
                    await self.close()
                    raise AuthorizationError from e
                elif isinstance(e, WSServerHandshakeError) and e.status == 404:
                    await self.close()
                    raise NodeUnknownError from e
                elif (
                        isinstance(e, ClientConnectorError)
                        or isinstance(e, ConnectionRefusedError)
                        or isinstance(e, ClientOSError)
                ):
                    pass
                else:
                    logger.error(f"Node ({self._node.identifier}) threw an error: {e} ({type(e).__name__})")

            if self.is_alive:
                logger.info(
                    f"Node {self._node.identifier} "
                    f"was success to successfully connect/reconnect to Lavalink V4 after "
                    f'{retries} connection attempts.'
                )
                self.dispatch("node_ready", self._node)

                await self._listen()
                break

            if self._retries <= retries:
                logger.debug(
                    f"{self._node.identifier} was unable to successfully connect/reconnect to Lavalink after "
                    f'{retries} connection attempt. This Node has exhausted the retry count.'
                )

                await self.close()
                break

            delay = min(3 * retries, 30)
            retries += 1

            logger.debug(f'Node ({self._node.identifier}) retrying websocket connection in {delay} seconds.')
            await sleep(delay)

    async def connect(self) -> None:
        self._node._status = NodeStatus.CONNECTING
        try:
            await self._connect_back()
        except Exception as e:
            logger.warning(f"Connection timeout to Lavalink V4: {e}")

    async def _handle_event(self, data: dict[any, any]) -> None:
        player = self._node.players.get(int(data['guildId']))  # type: ignore
        event_type = data['type']

        if not player:
            if event_type not in ('TrackEndEvent', 'WebSocketClosedEvent'):
                logger.warning(f"Player may have already be destroyed on node! ({self._node.identifier})")

            return

        if event_type == 'TrackStartEvent':
            self.dispatch(
                "track_start",
                player,
                player.queue.current
            )
        elif event_type == 'TrackEndEvent':
            end_reason = EndReason(data['reason'])
            self.dispatch(
                "track_end",
                player,
                player.queue.current,
                end_reason
            )
        elif event_type == 'TrackExceptionEvent':
            exception = data['exception']
            assert player.queue.current is not None

            self.dispatch(
                "track_exception",
                player,
                player.queue.current,
                exception['message'],
                Severity(exception['severity']),
                exception['cause']
            )
        elif event_type == 'TrackStuckEvent':
            assert player.queue.current is not None
            self.dispatch("track_stuck", player, player.queue.current, int(data['thresholdMs']))
        elif event_type == 'WebSocketClosedEvent':
            self.dispatch("discord_ws_closed", player, int(data['code']), data['reason'], bool(data['byRemote']))
        else:
            return self.dispatch("extra_event", event_type, player, data)

        if player and event_type in (
                'TrackStuckEvent',
                'TrackEndEvent'
        ):
            try:
                await player.handle_event(EndReason(data['reason']))
            except Exception as e:
                logger.error(f'Player {player.guild.id} threw an error whilst handling event : {e}')

    async def _handle_message(self, data: dict[any, any] | list[any]) -> None:
        if not isinstance(data, dict) or 'op' not in data:
            return

        if data['op'] == 'ready':
            self._node._status = NodeStatus.CONNECTED
            self._node._session_id = data['sessionId']

            await self._node.update_session(data["sessionId"], data["resumed"])
            self.dispatch('node_ready', self._node)
        elif data['op'] == 'stats':
            self._node.stats = Stats(self._node, data)
            self.dispatch('node_stats_update', self._node)
        elif data['op'] == 'playerUpdate':
            if player := self._node.players.get(int(data['guildId'])):
                await player.update_state(data['state'])
                self.dispatch('player_update', player)
        elif data["op"] == 'event':
            await self._handle_event(data)
        else:
            logger.warning(f"Node ({self._node.identifier}) received unhandled websocket op: {data['op']}")

    async def _listen(self) -> None:
        close_code: Optional[WSCloseCode] = None

        async for message in self._websocket:
            if message.type == WSMsgType.TEXT:
                await self._handle_message(message.json())
            elif message.type == WSMsgType.ERROR:
                exc = self._websocket.exception()
                logger.error(f'The node websocket ({self._node.identifier}) received an error: {exc}')
                close_code = WSCloseCode.INTERNAL_ERROR
                break
            elif message.type in (
                    WSMsgType.CLOSED,
                    WSMsgType.CLOSING,
                    WSMsgType.CLOSE
            ):
                close_code = message.data
                self._node.client.dispatch("connection_lost", self._node.client.voice_clients)
                await self.connect()
                break

        try:
            await self.connect()
        except Exception as e:
            ws_close_code = self._websocket.close_code
            if close_code is None and ws_close_code is not None:
                close_code = WSCloseCode(ws_close_code)

            await self.close(close_code or WSCloseCode.ABNORMAL_CLOSURE)
            logger.warning(f"Reconnecting failed closing with status ({ws_close_code}): {e}")

    def dispatch(self, name, *args) -> None:
        self._node.client.dispatch(f"harmonize_{name}", *args)

    async def close(self, code: WSCloseCode = WSCloseCode.OK) -> None:
        if self._websocket:
            try:
                await self._websocket.close(code=code)
            except Exception as e:
                logger.error(
                    f"While cleanup node ({self._node.identifier}) websocket "
                    f"threw an error: {e} ({type(e).__name__})"
                )

        await self._session.close()
        self._node._status = NodeStatus.DISCONNECTED
        self._node._session_id = None
        self._node._transport = None
        self._node.players.clear()

        logger.info(f"Successfully cleaned up the websocket for node ({self._node.identifier})")

    async def request(
            self,
            method: str,
            path: str,
            to: Optional[Serializable] = None,
            trace: bool = False,
            **kwargs
    ) -> any:
        if self._websocket.closed:
            raise IOError('Cannot instantiate any connections with a closed session!')

        if trace is True:
            kwargs['params'] = {**kwargs.get('params', {}), 'trace': 'true'}

        if path.startswith('/'):
            path = path[1:]

        try:
            async with self._session.request(
                    method=method,
                    url=self._http + "v4/" + path,
                    headers={'Authorization': self._password},
                    **kwargs
            ) as response:
                if response.status in (401, 403):
                    raise AuthenticationError

                if response.status == 200:
                    if to is str:
                        return await response.text()

                    json = await response.json()
                    return json if to is None else to.from_dict(json)

                if response.status == 204:
                    return True
        except Exception as original:
            raise ClientError from original
