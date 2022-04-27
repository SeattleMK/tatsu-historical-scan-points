"""
ScanChannel
"""

from types import NoneType
import discord

class ScanChannel:
    # https://discordpy.readthedocs.io/en/stable/api.html#discord.TextChannel.history
    """
    yaya
    """

    def __init__(
        self,
        channel: discord.TextChannel,
        limit: int = 100,
        user_history: dict = None,
    ) -> None:
        self.channel = channel
        self.limit = limit
        self.user_history = user_history
        if isinstance(self.user_history, NoneType):
            self.user_history = {}
        self.pause = False

    async def start_scan(self):
        await self.scan_channel()

    async def scan_channel(self):
        print(f"starting scan of {self.channel.name}")
        start_message = None
        end_message = None
        reached_end = False
        scan_total = 0
        while not reached_end:
            print(f"Scanned {scan_total} messages in {self.channel.name}", end="\r")
            if end_message:
                start_message = end_message
            end_message = await self.scan(start_message)
            scan_total += 100
            if end_message == start_message:
                reached_end = True
                print("done with scan")
        

    async def scan(self, start_message: discord.Message = None) -> discord.Message:
        last_message = None
        async for message in self.channel.history(before=start_message):
            if message.author.bot:
                continue
            author_id = message.author.id
            if not author_id in self.user_history:
                self.user_history[author_id] = 0
            self.user_history[author_id] += 1
            last_message = message
        if isinstance(last_message, NoneType):
            last_message = start_message
        return last_message