import discord
from discord.enums import ActivityType, Status
from discord.ext import commands, tasks

import asyncio
from logger import Logger

logger = Logger(__main__)

class PingActivity(commands.Cog):
      
    def __init__(self, bot):
            self.bot = bot
            
    async def _set_presence(self):
        status = self.bot.config.get("status")
        activity_type = self.bot.config.get("activity_type")
        url = None
        activity_message = (self.bot.config["activity_message"].format(ping)).strip()
        if activity_type is not None and not activity_message:
            logger.warning(
                'No activity message found whilst activity is provided, defaults to "Modmail".'
            )
            activity_message = "Modmail"

        if activity_type == ActivityType.listening:
            if activity_message.lower().startswith("to "):
                # The actual message is after listening to [...]
                # discord automatically add the "to"
                activity_message = activity_message[3:].strip()
        elif activity_type == ActivityType.streaming:
            url = self.bot.config["twitch_url"]

        if activity_type is not None:
            activity = discord.Activity(
                type=activity_type, name=activity_message, url=url
            )
        else:
            activity = None
        await self.bot.change_presence(activity=activity, status=status)

        return activity, status

    @tasks.loop(seconds=10)
    async def presence_loop(self):
        """Set presence to the configured value every 10 minutes."""
        logger.debug("Resetting presence.")
        await self._set_presence()

    @presence_loop.before_loop
    async def before_presence_loop(self):
        await self._set_presence()
        await asyncio.sleep(1)
            

def setup(bot):
    bot.add_cog(PingActivity(bot))
