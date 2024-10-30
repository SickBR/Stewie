import asyncio

import discord
from discord import slash_command, option
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, client):
        self.client = client

    @slash_command(description="Zeigt dir den Avatar eines Benutzers")
    @option(name="user", description="Benutzer", required=False)
    async def avatar(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        embed = discord.Embed(title=f"{member.name}'s avatar")
        embed.set_image(url=member.avatar)
        await ctx.respond(embed=embed)


def setup(client):
    client.add_cog(General(client))