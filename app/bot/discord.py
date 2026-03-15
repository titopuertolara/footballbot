import logging

import discord

from app.bot.handler import process_message
from app.config import settings

logger = logging.getLogger(__name__)


class JoinRequestView(discord.ui.View):
    """Discord buttons for accept/reject join requests."""

    def __init__(self, request_id: int, bot: "FootballBotClient"):
        super().__init__(timeout=None)
        self.request_id = request_id
        self.bot = bot

    @discord.ui.button(label="Aceptar", style=discord.ButtonStyle.green, emoji="✅")
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        response_text, metadata = await process_message(
            platform="discord",
            user_id=str(interaction.user.id),
            username=interaction.user.name,
            name=interaction.user.display_name,
            text=f"acepta la solicitud #{self.request_id}",
        )
        await interaction.edit_original_response(
            content=f"{interaction.message.content}\n\n✅ **Aceptado** — {response_text}",
            view=None,
        )

        if metadata and metadata.get("accepted_player"):
            accepted = metadata["accepted_player"]
            await self.bot.notify_player(
                player_platform_user_id=accepted["player_platform_user_id"],
                organizer_user_id=str(interaction.user.id),
                game_id=accepted.get("game_id", ""),
                accepted=True,
            )

    @discord.ui.button(label="Rechazar", style=discord.ButtonStyle.red, emoji="❌")
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        response_text, metadata = await process_message(
            platform="discord",
            user_id=str(interaction.user.id),
            username=interaction.user.name,
            name=interaction.user.display_name,
            text=f"rechaza la solicitud #{self.request_id}",
        )
        await interaction.edit_original_response(
            content=f"{interaction.message.content}\n\n❌ **Rechazado** — {response_text}",
            view=None,
        )

        if metadata and metadata.get("rejected_player"):
            rejected = metadata["rejected_player"]
            await self.bot.notify_player(
                player_platform_user_id=rejected["player_platform_user_id"],
                organizer_user_id=str(interaction.user.id),
                game_id=rejected.get("game_id", ""),
                accepted=False,
            )


class FootballBotClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)

    async def on_ready(self):
        logger.info(f"Discord bot logged in as {self.user}")

    async def notify_organizer(self, organizer_user_id: str, player_platform_user_id: str, game_id: int, game_location: str, game_date: str, game_time: str, request_id: int, position: str = None):
        """Send a DM to the organizer with accept/reject buttons."""
        try:
            user = await self.fetch_user(int(organizer_user_id))
            position_text = f" como **{position}**" if position else ""
            msg = (
                f"⚽ **Nueva solicitud para tu partido!**\n\n"
                f"<@{player_platform_user_id}> quiere unirse a tu partido #{game_id}{position_text}.\n"
                f"📍 {game_location} | 📅 {game_date} | 🕐 {game_time}"
            )

            view = JoinRequestView(request_id=request_id, bot=self)
            await user.send(msg, view=view)
            logger.info(f"Notified organizer {organizer_user_id} about join request #{request_id}")
        except Exception:
            logger.exception(f"Failed to notify organizer {organizer_user_id}")

    async def notify_player(self, player_platform_user_id: str, organizer_user_id: str, game_id: int, accepted: bool):
        """Send a DM to the player when their join request is accepted or rejected."""
        try:
            player_user = await self.fetch_user(int(player_platform_user_id))
            if accepted:
                msg = (
                    f"⚽ **¡Tu solicitud fue aceptada!**\n\n"
                    f"<@{organizer_user_id}> te aceptó en el partido #{game_id}.\n"
                    f"Contacta al organizador por DM para coordinar. ¡Nos vemos en la cancha!"
                )
            else:
                msg = (
                    f"⚽ **Tu solicitud fue rechazada**\n\n"
                    f"<@{organizer_user_id}> rechazó tu solicitud para el partido #{game_id}.\n"
                    f"¡No te desanimes! Busca otros partidos disponibles."
                )
            await player_user.send(msg)
            logger.info(f"Notified player {player_platform_user_id} about {'acceptance' if accepted else 'rejection'}")
        except Exception:
            logger.exception(f"Failed to notify player {player_platform_user_id}")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        # Only respond to DMs or when mentioned in a server channel
        is_dm = isinstance(message.channel, discord.DMChannel)
        is_mentioned = self.user in message.mentions if self.user else False

        if not is_dm and not is_mentioned:
            return

        text = message.content
        # Strip the mention from the message text if mentioned in a server
        if is_mentioned and self.user:
            text = text.replace(f"<@{self.user.id}>", "").strip()

        if not text:
            return

        try:
            async with message.channel.typing():
                response_text, metadata = await process_message(
                    platform="discord",
                    user_id=str(message.author.id),
                    username=message.author.name,
                    name=message.author.display_name,
                    text=text,
                )

            logger.info(f"Response to {message.author.name}: {response_text[:200]}")

            # Send DM notifications for join requests
            if metadata and metadata.get("notify_organizer"):
                notify = metadata["notify_organizer"]
                await self.notify_organizer(
                    organizer_user_id=notify["organizer_platform_user_id"],
                    player_platform_user_id=notify.get("player_platform_user_id", str(message.author.id)),
                    game_id=notify["game_id"],
                    game_location=notify.get("game_location", ""),
                    game_date=notify.get("game_date", ""),
                    game_time=notify.get("game_time", ""),
                    request_id=notify["request_id"],
                    position=notify.get("position"),
                )

            # Discord has a 2000 char limit per message
            if len(response_text) > 2000:
                for i in range(0, len(response_text), 2000):
                    await message.channel.send(response_text[i : i + 2000])
            else:
                await message.channel.send(response_text)

        except Exception:
            logger.exception("Error processing Discord message")
            await message.channel.send(
                "Sorry, something went wrong. Please try again."
            )


def run_discord_bot():
    client = FootballBotClient()
    client.run(settings.discord_token, log_handler=None)
