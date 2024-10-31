from datetime import datetime, timedelta

import aiosqlite
import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import random


class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client


    @slash_command(description="Zeigt dein aktuelles Guthaben")
    async def balance(self, ctx):
        db = self.client.get_cog('Database')
        coins = await db.get_coins(ctx.author, ctx.guild)

        embed = discord.Embed(title=f"{ctx.author.name}'s Guthaben", color=discord.Color.green())
        embed.add_field(name="Münzen", value=f"{coins} :moneybag:", inline=False)

        await ctx.respond(embed=embed)

    @slash_command(description="Hole dir deine tägliche Belohnung")
    async def daily(self, ctx):
        db = self.client.get_cog('Database')
        last_daily = await db.get_last_daily(ctx.author, ctx.guild)
        current_streak = await db.get_daily_streak(ctx.author, ctx.guild)

        if last_daily:
            last_daily = datetime.fromisoformat(last_daily)
            time_since_last_daily = datetime.utcnow() - last_daily
            if time_since_last_daily < timedelta(days=1):
                time_left = timedelta(days=1) - time_since_last_daily
                return await ctx.respond(
                    f"Du musst noch {time_left.seconds // 3600} Stunden und {(time_left.seconds // 60) % 60} Minuten warten!")
            elif time_since_last_daily > timedelta(days=2):
                current_streak = 0

        coins = 100 + (current_streak * 10)  # Base 100 coins + 10 for each day in the streak
        new_streak = current_streak + 1

        await db.add_coins(ctx.author, ctx.guild, coins)
        await db.update_last_daily(ctx.author, ctx.guild)
        await db.update_daily_streak(ctx.author, ctx.guild, new_streak)

        embed = discord.Embed(title="Tägliche Belohnung", color=discord.Color.gold())
        embed.add_field(name="Belohnung", value=f"{coins} :moneybag:", inline=False)
        embed.add_field(name="Streak", value=f"{new_streak} Tage", inline=False)
        embed.set_footer(text="Komm morgen wieder für mehr Münzen!")

        await ctx.respond(embed=embed)

    @slash_command(description="Zeigt dein Profil")
    async def profile(self, ctx):
        db = self.client.get_cog('Database')
        level, current_level_xp, xp_to_next_level = await db.get_level_xp(ctx.author, ctx.guild)
        coins = await db.get_coins(ctx.author, ctx.guild)
        streak = await db.get_daily_streak(ctx.author, ctx.guild)

        embed = discord.Embed(title=f"{ctx.author.name}'s Profil", color=discord.Color.purple())
        embed.set_thumbnail(url=ctx.author.avatar.url)

        embed.add_field(name="Level", value=level, inline=True)
        embed.add_field(name="Münzen", value=f"{coins} :moneybag:", inline=True)
        embed.add_field(name="Daily Streak", value=f"{streak} Tage", inline=False)

        progress = min(current_level_xp / xp_to_next_level, 1.0)
        progress_bar = "█" * int(10 * progress) + "░" * (10 - int(10 * progress))
        embed.add_field(name="Level Fortschritt", value=progress_bar, inline=False)

        await ctx.respond(embed=embed)

    @slash_command(description="Arbeite und verdiene Münzen")
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def work(self, ctx):
        db = self.client.get_cog('Database')

        # Liste der möglichen Jobs
        jobs = ["Programmierer", "Koch", "Lehrer", "Künstler", "Polizist"]
        job = random.choice(jobs)

        # Berechnung der verdienten Münzen
        coins = random.randint(50, 200)

        # Füge Münzen und XP hinzu
        await db.add_coins(ctx.author, ctx.guild, coins)
        await db.add_xp(ctx.author, ctx.guild, random.randint(10, 20))

        # Erstelle ein Embed für das Ergebnis
        embed = discord.Embed(
            title="Arbeit erledigt! 💼",
            description=f"Du hast als **{job}** gearbeitet und **{coins}** :moneybag: verdient!",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=ctx.author.avatar.url)  # Setzt das Benutzeravatar als Thumbnail
        embed.set_footer(text="Gute Arbeit! Weiter so!")

        # Sende das Embed als Antwort
        await ctx.respond(embed=embed)

    @slash_command(description="Zeigt die Top 10 Benutzer nach Münzen")
    async def leaderboard(self, ctx):
        db = self.client.get_cog('Database')

        async with aiosqlite.connect(db.DB) as conn:
            cursor = await conn.execute("""
                    SELECT user_id, coins FROM users 
                    WHERE guild_id = ? 
                    ORDER BY coins DESC 
                    LIMIT 10
                """, (ctx.guild.id,))
            top_users = await cursor.fetchall()

        if not top_users:
            return await ctx.respond("Es gibt noch keine Einträge im Leaderboard.")

        embed = discord.Embed(
            title="🏆 Top 10 Reichste Benutzer 🏆",
            color=discord.Color.gold(),
            description="Die wohlhabendsten Mitglieder unserer Community:"
        )

        for index, (user_id, coins) in enumerate(top_users, start=1):
            user = ctx.guild.get_member(user_id)
            if user:
                name = user.name
                if index == 1:
                    name = f"👑 {name}"
                elif index == 2:
                    name = f"🥈 {name}"
                elif index == 3:
                    name = f"🥉 {name}"
                else:
                    name = f"{index}. {name}"

                embed.add_field(
                    name=name,
                    value=f"{coins} :moneybag:",
                    inline=False
                )

        embed.set_footer(text="Weiter so! 💪 | Aktualisiert")
        embed.timestamp = datetime.utcnow()

        await ctx.respond(embed=embed)

    @slash_command(description="Wette deine Münzen")
    async def gamble(self, ctx, amount: Option(int, "Wie viele Münzen möchtest du setzen?", required=True)):
        db = self.client.get_cog('Database')
        user_coins = await db.get_coins(ctx.author, ctx.guild)

        if amount <= 0:
            return await ctx.respond("Du musst mindestens 1 Münze setzen!")
        if amount > user_coins:
            return await ctx.respond("Du hast nicht genug Münzen!")

        roll = random.randint(1, 100)
        result_message = ""
        coins_change = 0

        if roll <= 45:  # 45% Chance zu verlieren
            coins_change = -amount
            result_message = f"Du hast {amount} :moneybag: verloren!"
        elif roll <= 90:  # 45% Chance den Einsatz zu verdoppeln
            coins_change = amount
            result_message = f"Du hast {amount} :moneybag: gewonnen!"
        else:  # 10% Chance den Einsatz zu vervierfachen
            coins_change = amount * 3
            result_message = f"Jackpot! Du hast {amount * 3} :moneybag: gewonnen!"

        await db.add_coins(ctx.author, ctx.guild, coins_change)

        embed = discord.Embed(
            title="🎲 Glücksspiel 🎲",
            color=discord.Color.gold(),
            description=f"{ctx.author.mention} hat {amount} :moneybag: gesetzt!"
        )

        embed.add_field(name="Ergebnis", value=result_message, inline=False)
        embed.add_field(name="Würfel-Ergebnis", value=roll, inline=False)

        if coins_change > 0:
            embed.set_footer(text=f"Dein neues Guthaben: {user_coins + coins_change} :moneybag:")
        else:
            embed.set_footer(text=f"Dein Guthaben: {user_coins + coins_change}")

        await ctx.respond(embed=embed)





def setup(client):
    client.add_cog(Economy(client))
