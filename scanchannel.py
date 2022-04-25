"""
ScanChannel
"""

from dataclasses import field
import discord
from userhistory import UserHistory

class ScanChannel:
    # https://discordpy.readthedocs.io/en/stable/api.html#discord.TextChannel.history
    """
    yaya
    """

    def __init__(
        self,
        channel: discord.TextChannel,
        limit: int = 100,
        user_history: UserHistory = field(default_factory=UserHistory),
    ) -> None:
        self.channel = channel
        self.current_message = None
        self.limit = limit
        self.user_history = user_history

    def start_scan(self):
        if not self.current_message:
            self.current_message = self.channel.last_message
        self.scan(
            self.current_message
        )  # TODO replace with a method that keeps running repeatedly

    def stop_scan(self):  # TODO Destroy the object instead? This may not be necessary.
        pass

    def pause_scan(self):
        pass

    def scan(self, origin_message: discord.Message):
        messages_handled = 0
        for message in self.channel.history(origin_message, limit=self.limit):
            user_id = message.author.id
            if not user_id in self.user_history:
                self.user_history[user_id] = 0
            self.user_history[user_id] += 1
            messages_handled += 1
            if messages_handled == 100:
                self.current_message = message