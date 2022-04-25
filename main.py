"""
No
"""

from typing import Any
from dataclasses import dataclass, field
import configparser
import discord


def main():
    """
    Main method, executes at start
    """
    config = CustomConfig()
    config.read("config.ini")
    client = DiscordClient(config)
    client.run(config["discord"]["token"])


class CustomConfig(configparser.ConfigParser):
    """
    Modified ConfigParser to properly interpret the data of my config
    """

    def read(self, filenames: str, encoding: str = None):
        """
        Modified read methos to process values returned in the config instead of doing it later
        """
        configparser.ConfigParser.read(self, filenames, encoding)
        self["discord"]["guild"] = int(self["discord"]["guild"])
        self["discord"]["blocklist"] = map(
            int, str.split(self["discord"]["blocklist"], ",")
        )
        self["discord"]["moderator_role"] = int(self["discord"]["moderator_role"])


@dataclass
class UserHistory:
    """
    Stores each user's post count as a dataclass object
    """

    users: dict = {}

    def __setattr__(self, name: str, value: Any) -> None:
        self.users[name] = value

    def __getattr__(self, name: str) -> Any:
        return self.users[name]


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
        for message in self.channel.history(origin_message, limit=self.limit):
            user_id = message.author.id
            if not user_id in self.user_history:
                self.user_history[user_id] = 0
            self.user_history[user_id] += 1


class DiscordClient(discord.Client):
    """
    Modified discord.Client for the purpose of scanning for user messages across several channels
    of a discord.Guild
    """

    async def __init__(self, config: configparser.ConfigParser):
        discord.Client.__init__(self)
        self.history_config = config
        self.guild = self.get_guild(self.history_config["discord"]["guild"])
        self.moderator_role = self.history_config["discord"]["moderator_role"]

    async def on_ready(self):
        # pylint: disable=no-self-use
        """
        Event, when the Discord client is ready for things to happen beyond initial connection
        """
        print("ready to run")

    async def on_message(self, message: discord.Message):
        """
        Event, when a Discord message was sent
        """
        if hasattr(message, "guild"):
            if message.guild == self.history_config["discord"]["guild"]:
                await self.check_for_scan_message(message)

    async def check_for_scan_message(self, message: discord.Message):
        """
        It does stuff
        """
        if self.moderator_role in message.author.roles:
            if message.content.startswith("!scan"):
                match message.content.split()[1]:
                    case "on":
                        await self._start_scan_()
                    case "off":
                        await self._stop_scan_()
                    case "pause":
                        await self._pause_scan_()
                    case _:
                        await message.channel.send(
                            "Please specify an option: on, off, pause"
                        )

    async def _start_scan_(self):
        pass

    async def _pause_scan_(self):
        pass

    async def _stop_scan_(self):
        pass


if __name__ == "__main__":
    main()
