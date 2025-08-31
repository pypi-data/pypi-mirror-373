"""Fedinesia - deletes old statuses from fediverse accounts. This tool was previously
called MastodonAmnesia
Copyright (C) 2021, 2022, 2023  Mark S Burgunder.

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

import asyncio
import json
import sys
from datetime import datetime
from math import ceil
from pathlib import Path

import msgspec
import msgspec.json
import msgspec.toml
from httpx import AsyncClient
from loguru import logger as log
from minimal_activitypub import Status
from minimal_activitypub.client_2_server import ActivityPub
from minimal_activitypub.client_2_server import ActivityPubError
from minimal_activitypub.client_2_server import NetworkError
from minimal_activitypub.client_2_server import NotFoundError
from minimal_activitypub.client_2_server import RatelimitError
from stamina import retry_context
from tqdm import tqdm
from tqdm import trange
from whenever import Instant

from fedinesia import PROGRESS_ID_KEY
from fedinesia.config import Configuration
from fedinesia.util import AuditLog
from fedinesia.util import should_keep


class FediHelper(msgspec.Struct):
    """Class to contain logic for collecting statuses to be deleted."""

    audit_log: AuditLog
    config: Configuration
    oldest_to_keep: datetime
    instance: ActivityPub | None = None
    statuses: list[Status] = msgspec.field(default_factory=list)
    user_info: dict[str, str] | None = None

    async def connect(self) -> None:
        """Connect to Fedi instance."""
        client = AsyncClient(http2=True, timeout=30)

        self.instance = ActivityPub(
            instance=self.config.mastodon.instance,
            access_token=self.config.mastodon.access_token,
            client=client,
        )
        await self.instance.determine_instance_type()
        self.user_info = await self.instance.verify_credentials()

    async def retrieve_and_filter_statuses(
        self,
        continue_max_id: str | None = None,
        limit: int | None = None,
    ) -> None:
        """Retrieve all statuses for account."""
        max_id = continue_max_id
        pagination_progress = ""

        if not self.instance or not self.user_info:
            return

        log.opt(colors=True).info(
            f"We are removing statuses older than <cyan>{self.oldest_to_keep}</> "
            f"from <cyan>{self.config.mastodon.instance}@{self.user_info['username']}</> "
            f"with {self.user_info['statuses_count']} statuses"
        )

        while True:
            pagination_max_id = self.instance.pagination["next"]["max_id"]
            if pagination_max_id and pagination_progress and (pagination_max_id > pagination_progress):
                log.debug("Break")
                break

            max_id = self.determine_pagination(
                pagination_progress=pagination_progress,
                continue_max_id=continue_max_id,
            )

            try:
                log.debug(f"{max_id=}")
                statuses = await self.instance.get_account_statuses(
                    account_id=self.user_info["id"],
                    max_id=max_id,
                )
            except RatelimitError:
                await self.sleep_off_ratelimiting()

            log.debug(f"scrolling - {len(statuses)=}")
            if len(statuses) == 0:
                break

            log.debug(f"oldest_to_keep={self.oldest_to_keep.isoformat()}")
            self.statuses.extend(self._filter_statuses(statuses=statuses))
            log.debug(f"{len(self.statuses)=}")

            if limit and len(self.statuses) > limit:
                statuses_to_delete = self.statuses[:limit]
                self.statuses = statuses_to_delete
                log.debug(f"{len(self.statuses)=}")
                break

            last_status = statuses[-1]
            pagination_progress = last_status.get("id", "")
            log.debug(f"{pagination_progress=}")

    def determine_pagination(self, pagination_progress: str, continue_max_id: str | None) -> str | None:
        """Determine max_id for pagination while taking into account any potential saved progress."""
        if not self.instance or not self.user_info:
            log.error(f"Empty instance ({self.instance=}) or no user_info ({self.user_info=})")
            return None

        max_id = continue_max_id

        log.debug(f"{max_id=}")
        log.debug(f"{pagination_progress=}")
        log.debug(f"{self.instance.pagination=}")

        pagination_max_id = self.instance.pagination["next"]["max_id"]
        if not pagination_max_id:
            pagination_max_id = max_id
            log.debug(f"{pagination_max_id=}")

        if (not max_id) and pagination_progress:
            max_id = pagination_progress
            log.debug(f"{max_id=}")

        if max_id and pagination_max_id and max_id > pagination_max_id:
            max_id = pagination_max_id
            log.debug(f"{max_id=}")

        return max_id

    async def delete_statuses(
        self,
        save_progress_path: Path | None,
    ) -> None:
        """Delete all statuses that should be deleted."""
        log.info(
            f"A record of all deleted statuses will be recorded in the audit log file at {self.audit_log.audit_log}"
        )
        self.audit_log.begin()

        title = "Deleting statuses"
        total_statuses_to_delete = len(self.statuses)
        for status in tqdm(
            iterable=self.statuses,
            desc=f"{title:.<60}",
            ncols=120,
            total=total_statuses_to_delete,
            unit="statuses",
            position=0,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} at {rate_fmt}",
        ):
            try:
                for attempt in retry_context(on=NetworkError):
                    with attempt:
                        await self.delete_single_status(status=status)

                if save_progress_path:
                    last_deleted_id = status if isinstance(status, str) else status["id"]
                    with save_progress_path.open(mode="wb") as save_progress_file:
                        save_progress_file.write(msgspec.toml.encode({PROGRESS_ID_KEY: last_deleted_id}))
            except RatelimitError:
                await self.sleep_off_ratelimiting()

        self.audit_log.end()

        log.info(f"All old statuses deleted! Total of {len(self.statuses)} statuses deleted")

    async def delete_single_status(self, status: Status) -> None:
        """Delete  single status."""
        if not self.instance or not self:
            return

        log.debug(f"delete_single_status(status={status['id']}, instance={self.instance})")
        try:
            await self.instance.delete_status(status=status)
            log.debug(f"delete_single_status - Deleted status {status.get('url')} from {status.get('created_at')}")
            self.audit_log.add_entry(status=status)
        except NotFoundError:
            log.debug("Status for deletion not found. No problem then :)")
        except ActivityPubError as error:
            log.debug(f"delete_single_status - encountered error: {error}")
            log.debug(f"delete_single_status - status: {json.dumps(status, indent=4)}")
            raise error

    def delete_dry_run(self) -> None:
        """Print out what statuses would be deleted for a dry run."""
        log.opt(colors=True).info("--dry-run or -d specified. <yellow><bold>No statuses will be deleted</></>")
        for status in self.statuses:
            log.opt(colors=True).info(
                f"<red>Would</red> delete status {status.get('url')} from {status.get('created_at')}"
            )
        log.opt(colors=True).info(f"<bold>Total of {len(self.statuses)} statuses would be deleted.</>")

    def _filter_statuses(self, statuses: list[Status]) -> list[Status]:
        """Filter out statuses that should not be deleted."""
        deletion_list: list[Status] = []
        for status in statuses:
            if should_keep(status=status, oldest_to_keep=self.oldest_to_keep, config=self.config):
                continue

            deletion_list.append(status)

        log.debug(f"{len(deletion_list)=}")
        return deletion_list

    async def sleep_off_ratelimiting(self) -> None:
        """Wait for rate limiting to be over."""
        if not self.instance:
            log.error("Fedi instance not set, can't continue!")
            sys.exit(-1)

        log.debug(
            f"sleep_off_ratelimiting - Rate limited: Limit: {self.instance.ratelimit_remaining} - "
            f"resetting at: {self.instance.ratelimit_reset}"
        )
        now = Instant.now().py_datetime()
        need_to_wait = ceil((self.instance.ratelimit_reset - now).total_seconds())

        bar_title = f"Waiting until {self.instance.ratelimit_reset:%H:%M:%S %Z} to let server 'cool-down'"
        for _i in trange(
            need_to_wait,
            desc=f"{bar_title:.<60}",
            unit="s",
            ncols=120,
            bar_format="{desc}: {percentage:3.0f}%|{bar}| Eta: {remaining} - Elapsed: {elapsed}",
            position=1,
        ):
            await asyncio.sleep(1)
