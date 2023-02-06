"""
Validate that the pubkey is in your network

To enable, add this to your configuration file:

storage:
    validators:
        - nostr_relay.foaf.is_in_foaf

foaf:
    network_pubkeys: 
        - <your pubkey here>

See https://code.pobblelabs.org/fossil/nostr_relay/doc/tip/docs/foaf.md for all of the configuration options
"""


import logging

from aionostr import Manager
from nostr_relay.errors import StorageError
from nostr_relay.util import Periodic, json
from nostr_relay.config import Config


ALLOWED_PUBKEYS = set()


def is_in_foaf(event, config):
    """
    Check that the pubkey is in the configured social network
    """
    if config.foaf:
        if ALLOWED_PUBKEYS:
            if event.pubkey not in ALLOWED_PUBKEYS:
                raise StorageError(f"{event.pubkey} is not in my known network")


class FOAFBuilder(Periodic):
    """
    Periodically build the social network
    """

    def __init__(self):
        self.relay_urls = Config.foaf.get("check_relays", ["wss://nos.lol"])
        self.log = logging.getLogger("nostr_relay.foaf")
        self.network_levels = Config.foaf.get("levels", 1)
        self.seed_authors = Config.foaf.get(
            "network_pubkeys",
            ["c7da62153485ecfb1b65792c79ce3fe6fce6ed7d8ef536cb121d7a0c732e92df"],
        )
        self.save_file = Config.foaf.get("save_to", "/tmp/nostr-foaf.json")
        if self.save_file:
            loaded = self.load()
        else:
            loaded = False
        Periodic.__init__(
            self,
            Config.foaf.get("check_interval", 7200),
            swallow_exceptions=True,
            run_at_start=not loaded,
        )

    def load(self):
        import os.path

        if os.path.exists(self.save_file):
            with open(self.save_file, "r") as fp:
                network = json.load(fp)
            self.log.info(
                "Loaded network of %d pubkeys from %s", len(network), self.save_file
            )
            ALLOWED_PUBKEYS.update(set(network))
            return True

    async def run_once(self):
        find_query = {
            "kinds": [3],
            "authors": self.seed_authors,
        }
        network = set(self.seed_authors)
        async with Manager(self.relay_urls) as manager:
            self.log.info(
                "Getting following for %s from %s", self.seed_authors, self.relay_urls
            )
            async for event in manager.get_events(find_query):
                for tag in event.tags:
                    if tag[0] == "p":
                        network.add(tag[1])
            found = 1
            while found < self.network_levels:
                self.log.info("Getting extended network. Level %d", found)
                find_query["authors"] = list(network)
                async for event in manager.get_events(find_query):
                    for tag in event.tags:
                        if tag[0] == "p":
                            network.add(tag[1])
                found += 1

        self.log.info("Found network of %d pubkeys", len(network))
        ALLOWED_PUBKEYS.clear()
        ALLOWED_PUBKEYS.update(network)
        if self.save_file:
            with open(self.save_file, "w") as fp:
                json.dump(list(ALLOWED_PUBKEYS), fp)
            self.log.info("Saved network to %s", self.save_file)


Periodic.register(FOAFBuilder())
