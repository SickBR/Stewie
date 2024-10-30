import discord
from discord import slash_command, option
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @slash_command(description="Kick den Benutzer vom Server")
    @option(name="user", description="Benutzer", required=True)
    @option(name="reason", description="Grund", required=False)
    @discord.default_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if member is None:
            await ctx.respond("``wähl einen User zum kicken aus``")
            return

        embed = discord.Embed(title="Kick", description=f"{member.mention} wurde von dem Server gekickt.",
                              color=discord.Color.red())
        embed.add_field(name="Grund", value=reason)

        await member.kick(reason=reason)
        await ctx.respond(embed=embed, delete_after=10)

    @slash_command(description="Ban den Benutzer vom Server")
    @option(name="user", description="Benutzer", required=True)
    @option(name="reason", description="Grund", required=False)
    @discord.default_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        if member is None:
            await ctx.respond("``wähl einen User aus``.")
            return

        embed = discord.Embed(title="ban", description=f"{member.mention} wurde aus dem Server gebannt",
                              color=discord.Color.red())
        embed.add_field(name="Grund", value=reason)

        await member.ban(reason=reason)
        await ctx.respond(embed=embed, delete_after=10)

    @slash_command(description="Entbanne den Benutzer vom Server")
    @option(name="user", description="Benutzer", required=True)
    @discord.default_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        if member is None:
            await ctx.respond("``wähl einen User aus``")
            return

        embed = discord.Embed(title="Unban", description=f"{member} wurde entbannt")

        await member.unban()
        await ctx.respond(embed=embed, delete_after=10)

    @slash_command(description="Lösche eine bestimmte Anzahl an Nachrichten")
    @option(name="amount", description="Anzahl", required=False, type=int)
    @discord.default_permissions(manage_messages=True)
    async def clear(self, ctx, amount=5):
        if amount is None:
            await ctx.respond("``!Clear [Anzahl]``")
            return

        if amount > 200:
            await ctx.respond("``Die maximale Anzahl an Nachrichten die gelöscht werden können beträgt 200``")
            return

        await ctx.channel.purge(limit=amount)
        embed = discord.Embed(title="Clear", description=f"{amount} Nachrichten wurden gelöscht")

        await ctx.respond(embed=embed, delete_after=10)

    @slash_command(description="Lösche alle Nachrichten in einem Channel")
    @discord.default_permissions(manage_messages=True)
    async def purge(self, ctx):
        current_channel = ctx.channel
        channel_name = current_channel.name
        category = current_channel.category

        # Die Position des aktuellen Kanals in der Kategorie speichern
        channel_position = current_channel.position

        # Den aktuellen Kanal löschen
        await current_channel.delete()

        # Den neuen Kanal erstellen, indem du die Position des alten Kanals verwendest
        new_channel = await ctx.guild.create_text_channel(name=channel_name, category=category,
                                                          position=channel_position)

        embed = discord.Embed(title="Channel geleert", description="Der Channel wurde erfolgreich geleert.",
                              color=0x00ff00)

        await ctx.respond(embed=embed, delete_after=10)

    @slash_command(description="Setze den Slowchat")
    @option(name="seconds", description="Sekunden", required=True)
    @discord.default_permissions(manage_channels=True)
    async def slowchat(self, ctx, seconds: int):
        if seconds is None:
            await ctx.respond("``Es fehlen die angeforderten Sekunden für den Slowchat``")
            return

        await ctx.channel.edit(slowmode_delay=seconds)
        embed = discord.Embed(title="Slowchat", description=f"Slowchat wurde auf {seconds} Sekunden gesetzt.")

        await ctx.respond(embed=embed, delete_after=10)


def setup(client):
    client.add_cog(Moderation(client))
