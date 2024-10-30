import os

import discord
from discord.ext import commands

from dotenv import load_dotenv


# Load .env
load_dotenv()

# Setup Bot
intents = discord.Intents.all()
client = commands.Bot(
    command_prefix="!",
    intents=intents,
    status=discord.Status.online,
    activity=discord.Activity(type=discord.ActivityType.watching, name="mit /help alle Commands")
)
client.remove_command("help") 


# Setup on_ready method
@client.event
async def on_ready():
    print(f'------')
    print(f'Logged in as: {client.user.name} - {client.user.id}')
    print(f'Discord Version: {discord.__version__}')
    print(f'Pycord Version: {discord.__version__}')
    print(f'------')

    server_count = len(client.guilds)
    print(f'Der Bot ist auf {server_count} Servern aktiv:')

    for guild in client.guilds:
        print(f'- {guild.name} (id: {guild.id})')

    members = 0
    for guild in client.guilds:
        members += guild.member_count

    print(f'------')
    print(f'Total Members: {members}')
    print(f'------')
    print('Bot ist bereit!')


# Load Cogs
def load_cogs():
    for dir_path, dir_names, filenames in os.walk("./cogs"):
        for filename in filenames:
            if filename.endswith(".py"):
                relative_path = os.path.relpath(dir_path, ".")
                cog_path = f"{relative_path.replace(os.path.sep, '.')}.{filename[:-3]}"
                try:
                    client.load_extension(cog_path)
                    print(f"Loaded extension: {cog_path}")
                except Exception as e:
                    print(f"Failed to load extension {cog_path}: {e}")


# Run Main
def main():
    load_cogs()
    client.run(os.getenv("TOKEN"))


# Run Main if __name__ == "__main__"
if __name__ == "__main__":
    main()


