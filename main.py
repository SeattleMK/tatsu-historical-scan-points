"""
No
"""

from configparser import ConfigParser
from dataclasses import field
import discord
from customconfig import CustomConfig
from scanchannel import ScanChannel


def main():
    """
    Main method, executes at start
    """
    config = CustomConfig()
    config.read("config.ini")
    client = DiscordClient(config)
    client.run(config["discord"]["token"])


class DiscordClient(discord.Client):
    """
    Modified discord.Client for the purpose of scanning for user messages across several channels
    of a discord.Guild
    """

    def __init__(self, config: ConfigParser):
        self.history_config = config
        self.guild = field(default_factory=self.get_guild)
        self.moderator_role = field(default_factory=discord.Guild.get_role)
        discord.Client.__init__(self)

    async def on_ready(self):
        # pylint: disable=no-self-use
        """
        Event, when the Discord client is ready for things to happen beyond initial connection
        """
        print("ready to run")
        self.guild = self.get_guild(self.history_config.storage["discord"]["guild"])
        self.moderator_role = self.guild.get_role(
            role_id=self.history_config.storage["discord"]["moderator_role"]
        )

    async def on_message(self, message: discord.Message):
        """
        Event, when a Discord message was sent
        """
        if hasattr(message, "guild"):
            if message.guild.id == self.history_config.storage["discord"]["guild"]:
                await self.check_for_scan_message(message)

    async def check_for_scan_message(self, message: discord.Message):
        """
        It does stuff
        """
        if self.moderator_role in message.author.roles:
            message_split = message.content.split()
            if message.content.startswith("!scan"):
                if len(message_split) == 2:
                    match message_split[1]:
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
                else:
                    await message.channel.send(
                        "Please specify an option: on, off, pause"
                    )

    async def _start_scan_(self):
        print("start")

    async def _pause_scan_(self):
        print("pause")

    async def _stop_scan_(self):
        print("stop")


if __name__ == "__main__":
    main()
