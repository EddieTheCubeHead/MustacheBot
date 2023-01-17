import json

import discord
from discord import Client, Intents, Interaction
from discord.app_commands import CommandTree, describe

with open("settings.json", "r", encoding="utf-8") as settings_file:
    settings = json.loads(settings_file.read())

with open("secrets.json", "r", encoding="utf-8") as settings_file:
    token = json.loads(settings_file.read())["token"]


_GUILD = discord.Object(id=settings["guild"])


class Bot(Client):
    def __init__(self, description: str, intents: Intents):
        super().__init__(description=description, intents=intents)
        self.tree = CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=_GUILD)
        await self.tree.sync(guild=_GUILD)


def create_bot():
    description = "Use /help or /summon to get help into your room"
    intents = discord.Intents.default()
    return Bot(description, intents)


bot = create_bot()


@bot.event
async def on_ready():
    print("Connected")


@bot.tree.command(description="Ask for help", name="help")
@describe(room="The number or name of the room your team is in")
async def get_help(interaction: Interaction, room: str):
    admin_channel = interaction.guild.get_channel(settings["admin_channel"])
    await admin_channel.send(f"Help requested in room {room}")
    await interaction.response.send_message("Help request sent to the organizers.", ephemeral=True)


if __name__ == '__main__':
    bot.run(token)
