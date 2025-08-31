"""Helper classes and methods to assist with the general function of this bot.

Fedinesia - deletes old statuses for a fediverse account (Mastodon or Pleroma and forks)
Copyright (C) 2021, 2022, 2023  Mark S Burgunder

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
from pathlib import Path
from typing import TypeVar

import msgspec
import msgspec.json
import msgspec.toml
from httpx import AsyncClient
from minimal_activitypub import Visibility
from minimal_activitypub.client_2_server import ActivityPub
from minimal_activitypub.client_2_server import ActivityPubError

from fedinesia import CLIENT_WEBSITE
from fedinesia import USER_AGENT

BC = TypeVar("BC", bound="BotConfig")
ConfigClass = TypeVar("ConfigClass", bound="Configuration")
MC = TypeVar("MC", bound="MastodonConfig")


class BotConfig(msgspec.Struct):
    """Class holding configuration values for general behaviour of Fedinesia."""

    delete_after: int
    skip_deleting_pinned: bool = False
    skip_deleting_faved: bool = False
    skip_deleting_bookmarked: bool = False
    skip_deleting_poll: bool = False
    skip_deleting_visibility: list[Visibility] = []
    skip_deleting_media: bool = False
    skip_deleting_faved_at_least: int = 0
    skip_deleting_boost_at_least: int = 0
    skip_deleting_reactions_at_least: int = 0

    def get_config_values(self: BC) -> None:
        """Initialise instance."""
        self._get_delete_after()
        self._get_skip_bookmarked()
        self._get_skip_faved()
        self._get_skip_pinned()
        self._get_skip_poll()
        self._get_skip_dm()
        self._get_skip_media()
        self._get_skip_faved_at_least()
        self._get_skip_boost_at_lease()
        self._get_skip_reactions_at_lease()

    def _get_skip_poll(self: BC) -> None:
        """Private method to get skip deleting polls value from user if this
        value has not yet been configured.
        """
        print("Should polls be deleted when they get old enough?")
        y_or_n = input("[..] Please enter Y for yes or N for no: ")
        if y_or_n in ("Y", "y"):
            self.skip_deleting_poll = False
        elif y_or_n in ("N", "n"):
            self.skip_deleting_poll = True
        else:
            print("! ERROR ... please only respond with 'Y' or 'N'")
            print("! Cannot continue. Exiting now.")
            sys.exit(1)

    def _get_skip_dm(self: BC) -> None:
        """Private method to get skip deleting 'private' messages value from
        user if this value has not yet been configured.
        """
        print("Should Direct Messages be deleted when they get old enough?")
        y_or_n = input("[..] Please enter Y for yes or N for no: ")
        if y_or_n in ("Y", "y"):
            self.skip_deleting_visibility = []
        elif y_or_n in ("N", "n"):
            self.skip_deleting_visibility = [Visibility.DIRECT]
        else:
            print("! ERROR ... please only respond with 'Y' or 'N'")
            print("! Cannot continue. Exiting now.")
            sys.exit(1)

    def _get_skip_media(self: BC) -> None:
        """Private method to get skip deleting statuses with media value from
        user if this value has not yet been configured.
        """
        print("Should Statuses with attachments / pictures be deleted when they get old enough?")
        y_or_n = input("[..] Please enter Y for yes or N for no: ")
        if y_or_n in ("Y", "y"):
            self.skip_deleting_media = False
        elif y_or_n in ("N", "n"):
            self.skip_deleting_media = True
        else:
            print("! ERROR ... please only respond with 'Y' or 'N'")
            print("! Cannot continue. Exiting now.")
            sys.exit(1)

    def _get_skip_faved_at_least(self: BC) -> None:
        """Private method to get skip deleting statuses that have been
        favourited value from user if this value has not yet been
        configured.
        """
        print(
            "Should statuses being favourited a certain minimum number of times be "
            "excluded from deletion even when they get old enough?"
        )
        print("(enter 0 to disregard this setting)")
        self.skip_deleting_faved_at_least = int(input("[..] Please enter number: "))

    def _get_skip_boost_at_lease(self: BC) -> None:
        """Private method to get skip deleting statuses that have been
        boosted value from user if this value has not yet been configured.
        """
        print(
            "Should statuses being boosted a certain minimum number of times be "
            "excluded from deletion even when they get old enough?"
        )
        print("(enter 0 to disregard this setting)")
        self.skip_deleting_boost_at_least = int(input("[..] Please enter number: "))

    def _get_skip_reactions_at_lease(self: BC) -> None:
        """Private method to get skip deleting statuses that have been
        boosted value from user if this value has not yet been configured.
        """
        print(
            "Should statuses with a certain minimum number of reactions be "
            "excluded from deletion even when they get old enough?"
        )
        print("(enter 0 to disregard this setting)")
        self.skip_deleting_reactions_at_least = int(input("[..] Please enter number: "))

    def _get_skip_pinned(self: BC) -> None:
        """Private method to get skip deleting pinned statuses value from
        user if this value has not yet been configured.
        """
        print("Should pinned statuses be deleted when they get old enough?")
        y_or_n = input("[..] Please enter Y for yes or N for no: ")
        if y_or_n in ("Y", "y"):
            self.skip_deleting_pinned = False
        elif y_or_n in ("N", "n"):
            self.skip_deleting_pinned = True
        else:
            print("! ERROR ... please only respond with 'Y' or 'N'")
            print("! Cannot continue. Exiting now.")
            sys.exit(1)

    def _get_skip_faved(self: BC) -> None:
        """Private method to get skip deleting favorited statuses value from
        user if this value has not yet been configured.
        """
        print("Should favoured statuses be deleted when they get old enough?")
        y_or_n = input("[..] Please enter Y for yes or N for no: ")
        if y_or_n in ("Y", "y"):
            self.skip_deleting_faved = False
        elif y_or_n in ("N", "n"):
            self.skip_deleting_faved = True
        else:
            print("! ERROR ... please only respond with 'Y' or 'N'")
            print("! Cannot continue. Exiting now.")
            sys.exit(1)

    def _get_skip_bookmarked(self: BC) -> None:
        """Private method to get skip deleting bookmarked statuses from user
        if this value has not yet been configured.
        """
        print("Should bookmarked statuses be deleted when they get old enough?")
        y_or_n = input("[..] Please enter Y for yes or N for no: ")
        if y_or_n in ("Y", "y"):
            self.skip_deleting_bookmarked = False
        elif y_or_n in ("N", "n"):
            self.skip_deleting_bookmarked = True
        else:
            print("! ERROR ... please only respond with 'Y' or 'N'")
            print("! Cannot continue. Exiting now.")
            sys.exit(1)

    def _get_delete_after(self: BC) -> None:
        """Private method to get delete after value from user if this value
        has not yet been configured.
        """
        print('Please enter maximum age of retained statuses in the format of "number unit"')
        print('For example "1 weeks" or "3 days". Supported units are:')
        print(" - seconds\n - minutes\n - hours\n - days\n - weeks\n - months")
        max_age = input("[..] Minimum age to delete statuses (in seconds): ")
        max_age_parts = max_age.split(" ")
        max_age_number = int(max_age_parts[0])
        max_age_unit = max_age_parts[1]
        if max_age_unit == "seconds":
            self.delete_after = max_age_number
        elif max_age_unit == "minutes":
            self.delete_after = max_age_number * 3600
        elif max_age_unit == "hours":
            self.delete_after = max_age_number * 3600
        elif max_age_unit == "days":
            self.delete_after = max_age_number * 3600 * 24
        elif max_age_unit == "weeks":
            self.delete_after = max_age_number * 3600 * 24 * 7
        elif max_age_unit == "months":
            self.delete_after = max_age_number * 3600 * 24 * 30
        else:
            print("! Error ... unknown unit ({max_age_unit}) specified")
            print("! Cannot continue. Exiting now.")
            sys.exit(1)


class MastodonConfig(msgspec.Struct):
    """Class holding configuration values for Mastodon settings."""

    instance: str
    access_token: str

    @classmethod
    async def establish_new_mastodon_config(cls: type[MC]) -> MC:
        """Establish Mastodon configuration from scratch."""
        instance = input("[..] Enter instance (domain name) for Mastodon account host: ")

        try:
            async with AsyncClient(http2=True) as client:
                # Create app
                client_id, client_secret = await ActivityPub.create_app(
                    instance_url=instance,
                    client=client,
                    user_agent=USER_AGENT,
                    client_website=CLIENT_WEBSITE,
                )

                # Get Authorization Code / URL
                authorization_request_url = await ActivityPub.generate_authorization_url(
                    instance_url=instance,
                    client_id=client_id,
                    user_agent=USER_AGENT,
                )
                print(f"Please go to the following URL and follow the instructions:\n{authorization_request_url}")
                authorization_code = input("[...] Please enter the authorization code:")

                # Validate authorization code and get access token
                access_token = await ActivityPub.validate_authorization_code(
                    client=client,
                    instance_url=instance,
                    authorization_code=authorization_code,
                    client_id=client_id,
                    client_secret=client_secret,
                )

        except ActivityPubError as error:
            print(f"! Error when setting up Fediverse connection: {error}")
            print("! Cannot continue. Exiting now.")
            sys.exit(1)

        return cls(instance=instance, access_token=access_token)


class Configuration(msgspec.Struct):
    """Dataclass to hold all settings for fedinesia."""

    bot: BotConfig
    mastodon: MastodonConfig


async def setup_shop(
    config_file: str,
) -> Configuration:
    """Process command line arguments, establish debug logging to file if
    specified, load configuration.

    :returns:
        Configuration: config for this run of the Fedinesia.
    """
    config_file_path = Path(config_file)
    if config_file_path.exists():
        with config_file_path.open(mode="rb") as config_file_file:
            config: Configuration = msgspec.json.decode(config_file_file.read(), type=Configuration)

    else:
        bot = BotConfig(delete_after=30)
        bot.get_config_values()
        mastodon = await MastodonConfig.establish_new_mastodon_config()
        config = Configuration(bot=bot, mastodon=mastodon)

        config_encoded = msgspec.json.encode(config)
        config_json = msgspec.json.format(config_encoded, indent=4)
        with config_file_path.open(mode="wb") as config_file_file:
            config_file_file.write(config_json)

    return config
