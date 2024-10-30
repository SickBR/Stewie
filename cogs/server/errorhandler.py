import discord
from discord.ext import commands

class ErrorHandler(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await self.handle_cooldown_error(ctx, error)
        elif isinstance(error, commands.MissingRequiredArgument):
            await self.send_error_embed(ctx, "``Fehlende erforderliche Argumente", f"Fehlendes Argument: {error.param}``")
        elif isinstance(error, commands.MissingPermissions):
            await self.send_error_embed(ctx, "``Fehlende Berechtigungen", "Du hast nicht die erforderlichen Berechtigungen für diesen Befehl.``")
        elif isinstance(error, commands.BotMissingPermissions):
            await self.send_error_embed(ctx, "``Fehlende Bot-Berechtigungen", "Der Bot hat nicht die erforderlichen Berechtigungen für diesen Befehl.``")
        elif isinstance(error, commands.CommandNotFound):
            await self.send_error_embed(ctx, "``Befehl nicht gefunden", "Dieser Befehl existiert nicht.``")
        else:
            await self.send_error_embed(ctx, "``Unerwarteter Fehler", f"Ein unerwarteter Fehler ist aufgetreten: {error}``")
            print(f"Unerwarteter Fehler: {error}")  # Konsolenausgabe für Debugging

    async def handle_cooldown_error(self, ctx, error):
        retry_after = error.retry_after
        if retry_after < 60:
            time_format = f"{retry_after:.1f} Sekunden"
        elif retry_after < 3600:
            minutes = retry_after / 60
            time_format = f"{minutes:.1f} Minuten"
        elif retry_after < 86400:
            hours = retry_after / 3600
            time_format = f"{hours:.1f} Stunden"
        else:
            days = retry_after / 86400
            time_format = f"{days:.1f} Tagen"

        await self.send_error_embed(ctx, "Cooldown", f"``Dieser Befehl ist noch im Cooldown. Versuche es in {time_format} erneut.``")

    async def send_error_embed(self, ctx, title, description):
        embed = discord.Embed(title=f"❌ {title}", description=description, color=discord.Color.red())
        try:
            await ctx.respond(embed=embed, ephemeral=True)
        except:
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(ErrorHandler(client))