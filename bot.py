import json
import os

import discord
from discord import Client, Intents, Interaction, Role, User, Embed, Member
from discord.app_commands import CommandTree, describe
from discord.app_commands.checks import has_permissions


def get_config(config_name: str) -> str:
    config = os.getenv(config_name, None)
    if config is None:
        file_path = os.path.join(os.path.dirname(__file__), "settings.json")
        with open(file_path, "r", encoding="utf-8") as config_file:
            config = json.loads(config_file.read())[config_name]
    return str(config)


_GUILD = discord.Object(id=int(get_config("guild")))
_TEAM_ROOMS = {}


class Bot(Client):
    def __init__(self, description: str, intents: Intents):
        super().__init__(description=description, intents=intents)
        self.tree = CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=_GUILD)
        await self.tree.sync(guild=_GUILD)


def create_bot():
    description = "Use /help to get help into your room"
    intents = discord.Intents.default()
    return Bot(description, intents)


bot = create_bot()


@bot.event
async def on_ready():
    print("Connected")


@bot.tree.command()
@has_permissions(manage_roles=True)
async def register(interaction: Interaction, role: Role, room: str):
    _TEAM_ROOMS[role] = room
    await interaction.response.send_message(f"Room {room} assigned to role {role.name}")


@bot.tree.command(description="Ask for help", name="help")
@describe(message="Short description of your problem, can be empty")
async def get_help(interaction: Interaction, message: str):
    admin_channel = interaction.guild.get_channel(int(get_config("admin_channel")))
    room = _get_room(interaction.user)
    embed = Embed(title=f"Room {room}", description=message)
    embed.set_author(name="Help request")
    await admin_channel.send(embed=embed)
    await interaction.response.send_message("Help request sent to the organizers.", ephemeral=True)


def _get_room(user: Member) -> str:
    for role in user.roles:
        if role in _TEAM_ROOMS:
            return _TEAM_ROOMS[role]
    return "unknown"


if __name__ == '__main__':
    bot.run(get_config("token"))
