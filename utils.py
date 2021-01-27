import asyncio
import json

import asyncpg
import discord
import ssl
import os

with open('config.json') as f:
    config = json.load(f)

client = discord.Client()
discord_token = config['discord_token']

class DatabaseConnection(object):
    async def async_init(self):
        ctx = ssl.create_default_context(cafile='')
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.conn = await asyncpg.create_pool(user=config['database']['user'],
                                         password=config['database']['password'],
                                         database=config['database']['database'],
                                         host=config['database']['host'],
                                         ssl=ctx)
        
        await self.conn.execute('DROP TABLE IF EXISTS players')
        await self.conn.execute('''CREATE TABLE IF NOT EXISTS players (
            id bigint UNIQUE, channel bigint UNIQUE, name text, language text,
            trophies int DEFAULT 0, shards int DEFAULT 0,
            arena text DEFAULT 'beginning_arena',
            current_hero text DEFAULT 'fire_hero',
            current_melee text DEFAULT 'battle_axe',
            current_ranged text DEFAULT 'obsidian_spear',
            current_creature text DEFAULT 'mad_bomber',
            fire_hero json DEFAULT '{"level": 1, "xp": 0, "times_played": 0}',
            battle_axe json DEFAULT '{"level": 1, "xp": 0, "times_played": 0}',
            obsidian_spear json DEFAULT '{"level": 1, "xp": 0, "times_played": 0}',
            mad_bomber json DEFAULT '{"level": 1, "xp": 0, "times_played": 0}')
            ''')

    async def player_create(self, id, channel, name, language):
        return await self.conn.execute(
            '''INSERT INTO players (id, channel, name, language) VALUES ($1, $2, $3, $4)''',
            id, channel, name, language)

    async def player_get_data(self, id):
        return await self.conn.fetch('''SELECT * FROM players WHERE ID = $1''', id)
    
    async def player_columns(self):
        return await self.conn.fetch("SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'players'")

db = DatabaseConnection()

loop = asyncio.get_event_loop()
loop.run_until_complete(db.async_init())
