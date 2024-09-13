from typing import cast

from disnake import Intents, ApplicationCommandInteraction
from disnake.ext.commands import Bot, Param, slash_command, Cog

from harmonize.connection import Pool, Node
from harmonize.enums import CacheCapacity, LoopStatus
from harmonize.objects.filters import Timescale
from harmonize import Player


class Music(Cog):
    cog_unload = Pool.close_all

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        await self.bot.wait_until_ready()

        Pool.load_node(
            Node(
                client=self.bot,
                identifier="Test",
                host="localhost",
                port=2333,
                ssl=False,
                password="youshallnotpass",
                heartbeat=15.0,
                cache_capacity=CacheCapacity.MEDIUM
            )
        )

    @Cog.listener("on_ready")
    async def ready(self):
        print(f"Logged in as {self.bot.user} (ID: {self.bot.user.id})")

    @slash_command()
    async def play(
            self,
            interaction: ApplicationCommandInteraction,
            query: str,
            source: str = Param(
                choices={
                    "yandex": "ymsearch:",
                    "deezer": "dzsearch:",
                    "youtube": "ytmsearch:"
                },
                default=""
            )
    ) -> None:
        if load_search := await Pool.get_best_node().get_tracks(source + query):
            await interaction.response.defer(ephemeral=True)

            player: Player = cast(Player, interaction.guild.voice_client)
            if not player:
                player = await Player.connect_to_channel(interaction.author.voice.channel)

            player.queue.add(tracks=load_search.tracks[:3])
            await player.play()

            return await interaction.followup.send("Start playing")

        await interaction.response.send_message("Unknown track")

    @slash_command()
    async def disconnect(self, interaction: ApplicationCommandInteraction) -> None:
        vc: Player = cast(Player, interaction.guild.voice_client)
        if vc:
            await vc.disconnect()
            return await interaction.response.send_message("disconnected")
        await interaction.response.send_message("Not connected")

    @slash_command()
    async def current(self, interaction: ApplicationCommandInteraction) -> None:
        vc: Player = cast(Player, interaction.guild.voice_client)
        if vc:
            return await interaction.response.send_message(str(vc.queue.current))
        await interaction.response.send_message("Not connected")

    @slash_command()
    async def skip(self, interaction) -> None:
        vc: Player = interaction.guild.voice_client
        if vc:
            await vc.skip()
            return await interaction.response.send_message("Skipped")
        await interaction.response.send_message("Not connected")

    @slash_command()
    async def stop(self, interaction: ApplicationCommandInteraction) -> None:
        vc: Player = cast(Player, interaction.guild.voice_client)
        if vc:
            await vc.stop()
            return await interaction.response.send_message("Stopped")
        await interaction.response.send_message("Not connected")

    @slash_command()
    async def pause(self, interaction: ApplicationCommandInteraction) -> None:
        vc: Player = cast(Player, interaction.guild.voice_client)
        if vc:
            await vc.set_pause(True)
            return await interaction.response.send_message("Paused")
        await interaction.response.send_message("Not connected")

    @slash_command()
    async def resume(self, interaction: ApplicationCommandInteraction) -> None:
        vc: Player = cast(Player, interaction.guild.voice_client)
        if vc:
            await vc.set_pause(False)
            return await interaction.response.send_message("Resumed")
        return await interaction.response.send_message("Not connected")

    @slash_command()
    async def filter_on(self, interaction: ApplicationCommandInteraction) -> None:
        vc: Player = cast(Player, interaction.guild.voice_client)
        if vc:
            await vc.set_filters(filter=Timescale(speed=2, pitch=2, rate=2))
            return await interaction.response.send_message("Filter on")
        await interaction.response.send_message("Not connected")

    @slash_command()
    async def filter_off(self, interaction: ApplicationCommandInteraction) -> None:
        vc: Player = cast(Player, interaction.guild.voice_client)
        if vc:
            await vc.remove_filters()
            return await interaction.response.send_message("Filter removed")
        await interaction.response.send_message("Not connected")

    @slash_command()
    async def filter_update(self, interaction: ApplicationCommandInteraction) -> None:
        vc: Player = cast(Player, interaction.guild.voice_client)
        if vc:
            await vc.update_filters(filter=Timescale(speed=5, pitch=5, rate=5))
            return await interaction.response.send_message("Filter update")
        await interaction.response.send_message("Not connected")

    @slash_command()
    async def volume(self, interaction: ApplicationCommandInteraction, volume: int) -> None:
        vc: Player = cast(Player, interaction.guild.voice_client)
        if vc:
            await vc.change_volume(volume)
            return await interaction.response.send_message(f"Volume set to {volume}")
        await interaction.response.send_message("Not connected")

    @slash_command()
    async def loop_status(
            self,
            interaction: ApplicationCommandInteraction,
            status: int = Param(
                choices={
                    "off": 0,
                    "track": 1,
                    "queue": 2
                }
            )
    ) -> None:
        vc: Player = cast(Player, interaction.guild.voice_client)
        if vc:
            loop = LoopStatus(status)
            vc.queue.set_loop(loop)
            return await interaction.response.send_message(f"Loop status set to {loop}")
        await interaction.response.send_message("Not connected")

    @slash_command()
    async def queue(self, interaction: ApplicationCommandInteraction) -> None:
        vc: Player = cast(Player, interaction.guild.voice_client)
        if vc:
            return await interaction.response.send_message(
                "\n".join([f"{i + 1}. [{track}]({track.uri})" for i, track in enumerate(vc.queue.tracks)])
            )
        await interaction.response.send_message("Not connected")

    @slash_command()
    async def history(self, interaction: ApplicationCommandInteraction) -> None:
        vc: Player = cast(Player, interaction.guild.voice_client)
        if vc and vc.queue.history:
            return await interaction.response.send_message(
                "\n".join([f"{i + 1}. [{track}]({track.uri})" for i, track in enumerate(vc.queue.history)])
            )
        await interaction.response.send_message("Not connected")


client = Bot(intents=Intents.all(), command_prefix="!")
client.add_cog(Music(client))

client.run("YOUR_TOKEN_HERE")
