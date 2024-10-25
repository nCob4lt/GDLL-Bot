import discord
from discord.ext import commands

import clienttoken
from maincog import MainCog
from stats import StatsCog
from matchmaking import MatchmakingCog

class GDLL(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="ll!", intents=discord.Intents.all())

    async def setup_hook(self) -> None:
        await self.add_cog(MainCog(self))
        await self.add_cog(StatsCog(self))
        await self.add_cog(MatchmakingCog(self))
        
        await self.tree.sync()

bot = GDLL()
bot.run(clienttoken.clientToken.token)