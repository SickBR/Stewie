import discord
from discord.ext import commands
from discord import Option, SlashCommandGroup, Permissions
import asyncio

class TempVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.temp_channels = {}

    @commands.slash_command(
        name="tempvoice",
        description="Erstellt einen temporären Voice-Channel-Generator",
        default_member_permissions=Permissions(manage_channels=True)  # Nur User mit Channel-Management können den Command ausführen
    )
    @commands.has_permissions(manage_channels=True)  # Zusätzliche Permission-Check
    @commands.bot_has_permissions(
        manage_channels=True,  # Channel erstellen/löschen
        move_members=True,     # Member verschieben
        manage_roles=True      # Für Channel-Permissions
    )
    async def tempvoice(self, ctx):
        try:
            # Suche nach existierender Kategorie oder erstelle eine neue
            category = discord.utils.get(ctx.guild.categories, name="Temp Voice")
            if not category:
                category = await ctx.guild.create_category("⸻ [ User-Voice ] ⸻")

            # Erstelle den Hub-Channel mit Basis-Berechtigungen
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(
                    connect=True,
                    speak=True
                ),
                ctx.guild.me: discord.PermissionOverwrite(  # Bot-Berechtigungen
                    manage_channels=True,
                    move_members=True,
                    connect=True,
                    speak=True
                )
            }

            hub_channel = await ctx.guild.create_voice_channel(
                name="➕ Create Voice",
                category=category,
                user_limit=1,
                overwrites=overwrites
            )

            await ctx.respond("Temp Voice System wurde erstellt!", ephemeral=True)
        except discord.Forbidden:
            await ctx.respond("Ich habe nicht die nötigen Berechtigungen!", ephemeral=True)
        except Exception as e:
            await ctx.respond(f"Ein Fehler ist aufgetreten: {str(e)}", ephemeral=True)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        try:
            # Wenn ein User einem Voice Channel beitritt
            if after.channel and after.channel.name == "➕ Create Voice":
                # Erstelle einen neuen Voice Channel mit spezifischen Berechtigungen
                overwrites = {
                    member: discord.PermissionOverwrite(
                        manage_channels=True,
                        move_members=True,
                        connect=True,
                        speak=True,
                        view_channel=True
                    ),
                    member.guild.default_role: discord.PermissionOverwrite(
                        connect=True,
                        speak=True,
                        view_channel=True
                    ),
                    member.guild.me: discord.PermissionOverwrite(  # Bot-Berechtigungen
                        manage_channels=True,
                        move_members=True,
                        connect=True,
                        speak=True,
                        view_channel=True
                    )
                }

                new_channel = await after.channel.category.create_voice_channel(
                    name=f"🔊 {member.display_name}'s Channel",
                    overwrites=overwrites
                )

                # Bewege den User in den neuen Channel
                await member.move_to(new_channel)
                self.temp_channels[new_channel.id] = new_channel

            # Wenn ein User einen Voice Channel verlässt
            if before.channel and before.channel.id in self.temp_channels:
                if len(before.channel.members) == 0:
                    await before.channel.delete()
                    del self.temp_channels[before.channel.id]

        except discord.Forbidden:
            # Falls der Bot keine Berechtigung hat
            try:
                await member.send("Ich habe nicht die nötigen Berechtigungen, um temporäre Channel zu verwalten!")
            except:
                pass
        except Exception as e:
            print(f"Fehler in on_voice_state_update: {str(e)}")

def setup(bot):
    bot.add_cog(TempVoice(bot))