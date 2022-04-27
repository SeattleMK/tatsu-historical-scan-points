"""
No
"""

import requests
import time
from configparser import ConfigParser
from dataclasses import field
from collections import Counter
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
    results = client.final_results
    print("For emergency use, scraped data:")
    print(results)
    tatsu_api = Tatsu(config, results)
    tatsu_api.process_users()


class DiscordClient(discord.Client):
    """
    Modified discord.Client for the purpose of scanning for user messages across several channels
    of a discord.Guild
    """

    def __init__(self, config: ConfigParser):
        self.history_config = config
        self.final_results = Counter({})
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
            if message.content.startswith("!scan"):
                await self._start_scan_()

    async def _start_scan_(self):
        blocklist = self.history_config.storage["discord"]["blocklist"]
        for channel in self.guild.channels:
            if not channel.id in blocklist and isinstance(channel, discord.TextChannel):
                scanner = ScanChannel(channel)
                await scanner.start_scan()
                self.final_results += Counter(scanner.user_history)
        await self.close()


class Tatsu():# This is a lot of hackery, please do not use this anywhere, it's so bad
    def __init__(self, config: ConfigParser, user_data: list):
        self.config = config
        self.user_data = user_data
        self.base_url = f"{config['tatsu']['endpoint']}/guilds/{config['discord']['guild']}"
        self.api_restriction = 0
        self.api_reset = 0

    def set_request_limit(self, header: requests.models.CaseInsensitiveDict):
        if 'X-RateLimit-Remaining' in header:
            self.api_restriction = int(header['X-RateLimit-Remaining'])
            self.api_reset = int(header['X-RateLimit-Reset'])

    def can_request(self):
        if self.api_restriction == 0:
            current = int(time.time())
            while self.api_reset > current:
                sleep_time = self.api_reset - current
                print(f"Sleeping for {sleep_time}s due to API limits")
                time.sleep(sleep_time)
                current = int(time.time())

    def remove_user_score(self, member: int, score: int):
        self.can_request()
        url=f"{self.base_url}/members/{member}/score"
        headers={
            "Authorization": self.config["tatsu"]["token"],
            "Content-Type": "application/json"
        }
        body={
            "action": 1,
            "amount": score
        }
        result = requests.request('PATCH', url, json=body, headers=headers)
        self.set_request_limit(result.headers)
        return result

    def set_user_score(self, member: int, score: int):
        self.can_request()
        url=f"{self.base_url}/members/{member}/score"
        headers={
            "Authorization": self.config["tatsu"]["token"],
            "Content-Type": "application/json"
        }
        body={
            "action": 0,
            "amount": score
        }
        result = requests.request('PATCH', url, json=body, headers=headers)
        self.set_request_limit(result.headers)
        return result

    def get_user_score(self, member: int):
        self.can_request()
        url=f"{self.base_url}/rankings/members/{member}/all"
        headers={
            "Authorization": self.config["tatsu"]["token"],
            "Content-Type": "application/json"
        }
        result = requests.request('GET', url, headers=headers)
        self.set_request_limit(result.headers)
        score = None if not 'score' in result.json() else result.json()['score']
        return score

    def process_users(self):
        for user in self.user_data:
            score = self.get_user_score(user)
            if isinstance(score, int):
                print(f"setting score for {user}")
                print(f"- before: {score}")
                if score > 0:
                    remove_result = self.remove_user_score(user, score)
                    print(f"- post removal: {remove_result.json()['score']}")
                set_score = self.user_data[user]*int(self.config['tatsu']['multiplier'])
                if set_score > 100000:
                    print(f"- score was too high: {set_score}, lowering to 100000")
                    set_score = 100000
                set_result = self.set_user_score(user, set_score)
                print(f"- after: {set_result.json()['score']}")

if __name__ == "__main__":
    main()
