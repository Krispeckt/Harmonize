Events
======

Harmonize Events are events dispatched when certain events happen in Lavalink.
All events must be coroutines.

**For example:**

An event listener in a cog.

.. code-block:: python3

    @commands.Cog.listener()
    async def on_harmonize_node_ready(self, node: harmonize.connection.Node) -> None:
        ...

.. function:: on_harmonize_node_ready(node: harmonize.connection.Node)

        Called when the Node you are connecting to has initialised and successfully connected to Lavalink.

.. function:: on_harmonize_node_stats_update(node: harmonize.connection.Node)

        Called every minute when the ``stats`` OP is received by Lavalink.

.. function:: on_harmonize_player_update(player: harmonize.Player)

        Called when the ``playerUpdate`` OP is received from Lavalink.
        This event contains information about a specific connected player on the node.

.. function:: on_harmonize_track_start(player: harmonize.Player, track: harmonize.objects.Track)

        Called when a track starts playing.

.. function:: on_harmonize_track_end(player: harmonize.Player, track: harmonize.objects.Track, reason: harmonize.enums.EndReason)

        Called when the track finishes playing.

        .. warning::
            The library automatically plays the tracks in the queue!

.. function:: on_harmonize_track_exception(player: harmonize.Player, track: harmonize.objects.Track, message: str, severity: harmonize.enums.Severity, cause: str)

        Called when a track throws an exception.

.. function:: on_harmonize_track_stuck(player: harmonize.Player, track: harmonize.objects.Track, threshold: int)

        Called when a track gets stuck while playing.

.. function:: on_harmonize_discord_ws_closed(player: harmonize.Player, code: int, reason: str, by_remote: bool)

        Called when an audio WebSocket (to Discord) is closed. This can happen for various reasons (normal and abnormal), e.g. when using an expired voice server update.
        4xxx codes are usually bad.

        .. note::
            See the `Discord Docs <https://discord.com/developers/docs/topics/opcodes-and-status-codes#voice-voice-close-event-codes>`_.

.. function:: on_harmonize_session_no_longer(player: harmonize.Player)

        Called when an audio WebSocket (to Discord) is closed with code 4006.

        .. note::
            See the `Discord Docs <https://discord.com/developers/docs/topics/opcodes-and-status-codes#voice-voice-close-event-codes>`_.

.. function:: on_harmonize_session_timeout(player: harmonize.Player)

        Called when an audio WebSocket (to Discord) is closed with code 4009.

        .. note::
            See the `Discord Docs <https://discord.com/developers/docs/topics/opcodes-and-status-codes#voice-voice-close-event-codes>`_.

.. function:: on_harmonize_voice_modification(player: harmonize.Player)

        Called when an audio WebSocket (to Discord) is closed with code 4014.
        E.g., changed the voice channel or kicked out of the channel

        .. note::
            See the `Discord Docs <https://discord.com/developers/docs/topics/opcodes-and-status-codes#voice-voice-close-event-codes>`_.

.. function:: on_harmonize_voice_crashed(player: harmonize.Player)

        Called when an audio WebSocket (to Discord) is closed with code 4015.

        .. note::
            See the `Discord Docs <https://discord.com/developers/docs/topics/opcodes-and-status-codes#voice-voice-close-event-codes>`_.

.. function:: on_harmonize_extra_event(event_type: str, player: harmonize.Player, data: str)

        Called when an ``Unknown`` event is received via Lavalink. The payload includes the raw data sent from Lavalink.

        .. note::
            Please see the documentation for your Lavalink plugins to determine what data they send.

.. function:: on_harmonize_queue_end(player: harmonize.Player)

        Called when the track queue ends.

.. function:: on_harmonize_player_disconnect(player: harmonize.Player)

        Called when the player has been disconnected from the voice channel.