import discord
from discord.enums import ActivityType, Status
from discord.ext import commands

class PingActivity(commands.Cog):
      def __init__(self, bot):
            self.bot = bot
            
    @commands.command(aliases=["presence"])
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def activity(self, ctx, activity_type: str.lower, *, message: str = ""):
        """
        Set an activity status for the bot.

        Possible activity types:
            - `playing`
            - `streaming`
            - `listening`
            - `watching`

        When activity type is set to `listening`,
        it must be followed by a "to": "listening to..."

        When activity type is set to `streaming`, you can set
        the linked twitch page:
        - `{prefix}config set twitch_url https://www.twitch.tv/somechannel/`

        To remove the current activity status:
        - `{prefix}activity clear`
        """
        if activity_type == "clear":
            self.bot.config.remove("activity_type")
            self.bot.config.remove("activity_message")
            await self.bot.config.update()
            await self.set_presence()
            embed = discord.Embed(title="Activity Removed", color=self.bot.main_color)
            return await ctx.send(embed=embed)

        if not message:
            raise commands.MissingRequiredArgument(SimpleNamespace(name="message"))

        try:
            activity_type = ActivityType[activity_type]
        except KeyError:
            raise commands.MissingRequiredArgument(SimpleNamespace(name="activity"))

        activity, _ = await self.set_presence(
            activity_type=activity_type, activity_message=message
        )

        self.bot.config["activity_type"] = activity.type.value
        self.bot.config["activity_message"] = activity.name
        await self.bot.config.update()

        msg = f"Activity set to: {activity.type.name.capitalize()} "
        if activity.type == ActivityType.listening:
            msg += f"to {activity.name}."
        else:
            msg += f"{activity.name}."

        embed = discord.Embed(
            title="Activity Changed", description=msg, color=self.bot.main_color
        )
        return await ctx.send(embed=embed)

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def status(self, ctx, *, status_type: str.lower):
        """
        Set a status for the bot.

        Possible status types:
            - `online`
            - `idle`
            - `dnd` or `do not disturb`
            - `invisible` or `offline`

        To remove the current status:
        - `{prefix}status clear`
        """
        if status_type == "clear":
            self.bot.config.remove("status")
            await self.bot.config.update()
            await self.set_presence()
            embed = discord.Embed(title="Status Removed", color=self.bot.main_color)
            return await ctx.send(embed=embed)

        status_type = status_type.replace(" ", "_")
        try:
            status = Status[status_type]
        except KeyError:
            raise commands.MissingRequiredArgument(SimpleNamespace(name="status"))

        _, status = await self.set_presence(status=status)

        self.bot.config["status"] = status.value
        await self.bot.config.update()

        msg = f"Status set to: {status.value}."
        embed = discord.Embed(
            title="Status Changed", description=msg, color=self.bot.main_color
        )
        return await ctx.send(embed=embed)

    async def set_presence(
        self, *, status=None, activity_type=None, activity_message=None
    ):

        if status is None:
            status = self.bot.config.get("status")

        if activity_type is None:
            activity_type = self.bot.config.get("activity_type")

        url = None
        activity_message = (
            activity_message or self.bot.config["activity_message"]
        ).strip()
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

    @tasks.loop(minutes=30)
    async def loop_presence(self):
        """Set presence to the configured value every 30 minutes."""
        logger.debug("Resetting presence.")
        await self.set_presence()

    @loop_presence.before_loop
    async def before_loop_presence(self):
        await self.bot.wait_for_connected()
        logger.line()
        activity, status = await self.set_presence()

        if activity is not None:
            msg = f"Activity set to: {activity.type.name.capitalize()} "
            if activity.type == ActivityType.listening:
                msg += f"to {activity.name}."
            else:
                msg += f"{activity.name}."
            logger.info(msg)
        else:
            logger.info("No activity has been set.")
        if status is not None:
            msg = f"Status set to: {status.value}."
            logger.info(msg)
        else:
            logger.info("No status has been set.")

        await asyncio.sleep(1800)
        logger.info("Starting presence loop.")

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    @utils.trigger_typing
    async def ping(self, ctx):
        """Pong! Returns your websocket latency."""
        embed = discord.Embed(
            title="Pong! Websocket Latency:",
            description=f"{self.bot.ws.latency * 1000:.4f} ms",
            color=self.bot.main_color,
        )
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(PingActivity(bot))
