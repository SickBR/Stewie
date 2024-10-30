import asyncio
import random

import aiosqlite
import discord
from discord.ext import commands
import math

class Database(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.DB = "users.db"

    @commands.Cog.listener()
    async def on_ready(self):
        async with aiosqlite.connect(self.DB) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER,
                    guild_id INTEGER,
                    coins INTEGER DEFAULT 0,
                    bank INTEGER DEFAULT 0,
                    xp INTEGER DEFAULT 0,
                    last_daily TIMESTAMP,
                    daily_streak INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, guild_id)
                )
            """)
            await db.commit()

    async def add_xp(self, user, guild, xp_amount):
        async with aiosqlite.connect(self.DB) as db:
            await db.execute("""
                INSERT INTO users (user_id, guild_id, xp) 
                VALUES (?, ?, ?) 
                ON CONFLICT(user_id, guild_id) 
                DO UPDATE SET xp = xp + ?
            """, (user.id, guild.id, xp_amount, xp_amount))
            await db.commit()

    async def get_xp(self, user, guild):
        async with aiosqlite.connect(self.DB) as db:
            cursor = await db.execute("SELECT xp FROM users WHERE user_id = ? AND guild_id = ?", (user.id, guild.id))
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def add_coins(self, user, guild, amount):
        async with aiosqlite.connect(self.DB) as db:
            await db.execute("""
                INSERT INTO users (user_id, guild_id, coins) 
                VALUES (?, ?, ?) 
                ON CONFLICT(user_id, guild_id) 
                DO UPDATE SET coins = coins + ?
            """, (user.id, guild.id, amount, amount))
            await db.commit()

    async def get_coins(self, user, guild):
        async with aiosqlite.connect(self.DB) as db:
            cursor = await db.execute("SELECT coins FROM users WHERE user_id = ? AND guild_id = ?", (user.id, guild.id))
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def update_last_daily(self, user, guild):
        async with aiosqlite.connect(self.DB) as db:
            await db.execute("""
                UPDATE users SET last_daily = CURRENT_TIMESTAMP
                WHERE user_id = ? AND guild_id = ?
            """, (user.id, guild.id))
            await db.commit()

    async def get_last_daily(self, user, guild):
        async with aiosqlite.connect(self.DB) as db:
            cursor = await db.execute("SELECT last_daily FROM users WHERE user_id = ? AND guild_id = ?",
                                      (user.id, guild.id))
            result = await cursor.fetchone()
            return result[0] if result else None

    async def get_daily_streak(self, user, guild):
        async with aiosqlite.connect(self.DB) as db:
            cursor = await db.execute("SELECT daily_streak FROM users WHERE user_id = ? AND guild_id = ?",
                                      (user.id, guild.id))
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def update_daily_streak(self, user, guild, streak):
        async with aiosqlite.connect(self.DB) as db:
            await db.execute("""
                UPDATE users SET daily_streak = ?
                WHERE user_id = ? AND guild_id = ?
            """, (streak, user.id, guild.id))
            await db.commit()

    async def get_top_users(self, guild, limit=10):
        async with aiosqlite.connect(self.DB) as db:
            cursor = await db.execute("""
                SELECT user_id, xp, coins FROM users 
                WHERE guild_id = ? 
                ORDER BY xp DESC 
                LIMIT ?
            """, (guild.id, limit))
            return await cursor.fetchall()

    def calculate_level_and_progress(self, xp):
        # Calculate the level using the XP
        level = max(1, math.floor(0.1 * math.sqrt(xp)))

        # Calculate XP for the current level and the next level
        xp_for_current_level = 100 * (level ** 2)
        xp_for_next_level = 100 * ((level + 1) ** 2)

        # Return the level, current XP, and XP needed for the next level
        return level, xp - xp_for_current_level, xp_for_next_level - xp_for_current_level

    async def get_level_xp(self, user, guild):
        xp = await self.get_xp(user, guild)
        return self.calculate_level_and_progress(xp)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        db = self.client.get_cog('Database')

        async with aiosqlite.connect(db.DB) as conn:
            await conn.execute("""
                   INSERT OR IGNORE INTO users (user_id, guild_id)
                   VALUES (?, ?)
               """, (message.author.id, message.guild.id))
            await conn.commit()

        xp_gain = random.randint(15, 25)
        await db.add_xp(message.author, message.guild, xp_gain)

        old_level, _, _ = db.calculate_level_and_progress(await db.get_xp(message.author, message.guild) - xp_gain)
        new_level, _, _ = db.calculate_level_and_progress(await db.get_xp(message.author, message.guild))

        if new_level > old_level:
            coins_reward = new_level * 100
            await db.add_coins(message.author, message.guild, coins_reward)

            embed = discord.Embed(
                title="🎉 Level Up! 🎉",
                description=f"Glückwunsch, {message.author.mention}!",
                color=discord.Color.gold()
            )
            embed.add_field(name="Neues Level", value=str(new_level), inline=True)
            embed.add_field(name="Belohnung", value=f"{coins_reward} :coin:", inline=True)
            embed.set_thumbnail(url=message.author.avatar.url)
            embed.set_footer(text="Weiter so! 💪")

            level_up_message = await message.channel.send(embed=embed)

            await asyncio.sleep(15)
            await level_up_message.delete()

def setup(client):
    client.add_cog(Database(client))