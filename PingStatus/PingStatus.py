import discord
from discord.enums import ActivityType, Status
from discord.ext import commands, tasks
import logging

logger = logging.getLogger("Modmail")

class PingActivity(commands.Cog):
      
    def __init__(self, bot):
            self.bot = bot
            
    async def _set_presence(self):
        await bot.change_presence(status=discord.Status.online, activity=discord.Activity(name=f"testù {len(bot.guilds)}", type=discord.ActivityType.streaming, url="https://twitch.tv/testu"))

    @tasks.loop(seconds=10)
    async def presence_loop(self):
        """Set presence to the configured value every 10 minutes."""
        logger.debug("Resetting presence.")
        await self._set_presence()

    @presence_loop.before_loop
    async def before_presence_loop(self):
        await self._set_presence()
        await self.bot.wait_until_ready()

    async def on_ready(self):
        """testù"""
    #await self._set_presence()
    logger.debug("testù")
    presence_loop
            

def setup(bot):
    bot.add_cog(PingActivity(bot))
