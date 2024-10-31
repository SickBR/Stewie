import datetime

import discord
from discord import slash_command, option, Option
from discord.ext import commands

from main import client


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

    @slash_command(name="mute", description="Schaltet einen User stumm")
    @commands.has_permissions(moderate_members=True)
    async def mute(
            self, ctx,
            member: Option(discord.Member, "Wähle einen User zum stummschalten"),
            reason: Option(str, "Grund für den Mute", required=False, default="Kein Grund angegeben")
    ):
        if ctx.author.top_role <= member.top_role:  # Hier war self.ctx falsch
            await ctx.respond("Du kannst keine Mitglieder muten, die eine höhere oder gleiche Rolle wie du haben!")
            return


        try:
            # Hier fügen wir eine tatsächliche Timeout-Dauer hinzu (z.B. 1 Woche)
            await member.timeout(duration=discord.utils.utcnow() + datetime.timedelta(days=7), reason=reason)
            embed = discord.Embed(
                title="User gemuted",
                description=f"{member.mention} wurde von {ctx.author.mention} gemuted.\nGrund: {reason}",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed)
        except discord.Forbidden:
            await ctx.respond("Ich habe nicht die nötigen Rechte, um diesen User zu muten!")
        except Exception as e:
            await ctx.respond(f"Ein Fehler ist aufgetreten: {str(e)}")

    @slash_command(name="unmute", description="Hebt den Mute eines Users auf")
    @commands.has_permissions(moderate_members=True)
    async def unmute(
            self, ctx,
            member: Option(discord.Member, "Wähle einen User zum entstummen"),
            reason: Option(str, "Grund für den Unmute", required=False, default="Kein Grund angegeben")
    ):
        if ctx.author.top_role <= member.top_role:  # Hier war self.ctx falsch
            await ctx.respond("Du kannst keine Mitglieder unmuten, die eine höhere oder gleiche Rolle wie du haben!")
            return

        try:
            await member.timeout(duration=None, reason=reason)
            embed = discord.Embed(
                title="User unmuted",
                description=f"{member.mention} wurde von {ctx.author.mention} entmuted.\nGrund: {reason}",
                color=discord.Color.green()
            )
            await ctx.respond(embed=embed)
        except discord.Forbidden:
            await ctx.respond("Ich habe nicht die nötigen Rechte, um diesen User zu unmuten!")
        except Exception as e:
            await ctx.respond(f"Ein Fehler ist aufgetreten: {str(e)}")



def setup(client):
    client.add_cog(Moderation(client))
