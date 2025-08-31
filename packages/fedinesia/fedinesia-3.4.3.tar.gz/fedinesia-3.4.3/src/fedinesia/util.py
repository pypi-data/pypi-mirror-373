"""Fedinesia - deletes old statuses for a fediverse account (Mastodon or Pleroma and forks)
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

import csv
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
from typing import TypeVar

from loguru import logger as log
from minimal_activitypub.client_2_server import Status
from whenever import Instant

from fedinesia import __display_name__
from fedinesia.config import Configuration

logger = logging.getLogger(__display_name__)


AL = TypeVar("AL", bound="AuditLog")


@dataclass
class AuditLog:
    """Class to control the creation of an audit log and adding entries to
    it.
    """

    class Style(str, Enum):
        """Enumerating different audit log file styles implemented."""

        PLAIN = "PLAIN"
        CSV = "CSV"

    audit_log: Path | None
    style: Style = Style.PLAIN
    _audit_log_file: Any | None = None

    def begin(self: AL) -> None:
        """Open audit log file for writing and appending new log entries."""
        if not self.audit_log:
            return

        self._audit_log_file = self.audit_log.open(mode="at")

        if self.style == AuditLog.Style.CSV and os.fstat(self._audit_log_file.fileno()).st_size == 0:  # type: ignore[attr-defined]
            self._add_csv_header()

    def end(self: AL) -> None:
        """Close audit log file."""
        if self._audit_log_file:
            self._audit_log_file.close()

    def add_entry(self: AL, status: Status) -> None:
        """Append an entry/status details to the audit log file."""
        if self.style == AuditLog.Style.PLAIN:
            self._add_plain_entry(status)
        elif self.style == AuditLog.Style.CSV:
            self._add_csv_entry(status)

    def _add_plain_entry(self: AL, status: Status) -> None:
        """Append a plain text entry/status details to the audit log file."""
        if not self._audit_log_file:
            return

        entry = (
            f"{datetime.now():%Y-%m-%d %H:%M:%S%z} -"
            f" Removed {'poll' if status.get('poll', False) else 'status'} {status.get('url')}"
            f" created @ {status.get('created_at')}"
            f" with {status.get('visibility')} visibility, {len(status.get('media_attachments', []))} attachments."
            f" This status was reblogged {status.get('reblogs_count')} times and"
            f" favourited {status.get('favourites_count')} times."
            f" The status was {'pinned' if status.get('pinned') else 'not pinned'}.\n"
        )
        self._audit_log_file.write(entry)

    def _add_csv_entry(self: AL, status: Status) -> None:
        """Append a csv formatted status details to the audit log file."""
        if not self._audit_log_file:
            return

        csv_writer = csv.writer(self._audit_log_file, quoting=csv.QUOTE_ALL)
        record = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S%z"),
            "poll" if status.get("poll", False) else "status",
            status.get("url"),
            Instant.parse_common_iso(status.get("created_at", "0")).py_datetime(),
            status.get("visibility"),
            len(status.get("media_attachments", [])),
            status.get("reblogs_count"),
            status.get("favourites_count"),
            status.get("pinned"),
        ]
        csv_writer.writerow(record)

    def _add_csv_header(self: AL) -> None:
        """Write CSV header line to the audit log file.

        This method is normally called when an audit log file is being
        initially created before writing any other entries to the audit
        log; i.e. The record it writes will be the header record for the
        CSV file.
        """
        if not self._audit_log_file:
            return

        csv_writer = csv.writer(self._audit_log_file, quoting=csv.QUOTE_ALL)
        record = [
            "date and time of deletion",
            "type of status,",
            "url of status before deletion",
            "date and time deleted status was created",
            "visibility",
            "# of media_attachments",
            "reblogs_count",
            "favourites_count",
            "pinned",
        ]
        csv_writer.writerow(record)


def _is_status_too_recent(status: Status, oldest_to_keep: datetime) -> bool:
    """Check if status is too young to delete."""
    status_created_at = Instant.parse_common_iso(status.get("created_at", "0")).py_datetime()
    if status_created_at >= oldest_to_keep:
        log.debug(f"{status.get('id')} posted at {status.get('created_at')}")
        return True

    return False


def _is_self_bookmarked(status: Status, config: Configuration) -> bool:
    """Check if the status has been bookmarked by the original poster and bookmarked statuses should be kept."""
    if config.bot.skip_deleting_bookmarked and bool(status.get("bookmarked")):
        return True

    return False


def _is_self_favourite(status: Status, config: Configuration) -> bool:
    """Check if the status has been favoured by the original poster and favoured statuses should be kept."""
    if config.bot.skip_deleting_faved and bool(status.get("favourited")):
        return True

    return False


def _is_pinned(status: Status, config: Configuration) -> bool:
    """Check if the status has been pinned and pinned statuses should be kept."""
    if config.bot.skip_deleting_pinned and bool(status.get("pinned")):
        return True

    return False


def _is_poll(status: Status, config: Configuration) -> bool:
    """Check if the status is a poll and if polls should be kept."""
    if config.bot.skip_deleting_poll and bool(status.get("poll")):
        return True

    return False


def _matches_visibility(status: Status, config: Configuration) -> bool:
    """Check if the status visibility matches any visibility that should be kept."""
    if status.get("visibility") in config.bot.skip_deleting_visibility:
        return True

    return False


def _has_media(status: Status, config: Configuration) -> bool:
    """Check if status includes media and if statuses with media should be kept."""
    medias = status.get("media_attachments")
    if config.bot.skip_deleting_media and isinstance(medias, list) and bool(len(medias)):
        return True

    return False


def _has_enough_favourites(status: Status, config: Configuration) -> bool:
    """Check if status has been favoured more often than defined for keeping favoured statuses."""
    favourites = status.get("favourites_count", 0)
    if config.bot.skip_deleting_faved_at_least and favourites >= config.bot.skip_deleting_faved_at_least:
        return True

    return False


def _has_enough_reblogs(status: Status, config: Configuration) -> bool:
    """Check if status has been reblogged more often than defined for keeping reblogged statuses."""
    reblogs = status.get("reblogs_count", 0)
    if config.bot.skip_deleting_boost_at_least and reblogs >= config.bot.skip_deleting_boost_at_least:
        return True

    return False


def should_keep(status: Status, oldest_to_keep: datetime, config: Configuration) -> bool:
    """Determine if status should be kept."""
    keep_rules: list[bool] = [
        _is_status_too_recent(status=status, oldest_to_keep=oldest_to_keep),
        _is_self_bookmarked(status=status, config=config),
        _is_self_favourite(status=status, config=config),
        _is_pinned(status=status, config=config),
        _is_poll(status=status, config=config),
        _matches_visibility(status=status, config=config),
        _has_media(status=status, config=config),
        _has_enough_favourites(status=status, config=config),
        _has_enough_reblogs(status=status, config=config),
    ]

    if any(keep_rules):
        return True

    if config.bot.skip_deleting_reactions_at_least:
        reactions_threshold = config.bot.skip_deleting_reactions_at_least
    else:
        reactions_threshold = 0

    return enough_reactions_to_keep(
        status=status,
        reactions_threshold=reactions_threshold,
    )


def enough_reactions_to_keep(status: Status, reactions_threshold: int) -> bool:
    """Check if emoji_reactions are reported in status and check of they are at least at the
    threshold for keeping the status.
    Note: Reactions are a Pleroma specific feature.

    :param status: Status being examined for reactions
    :param reactions_threshold: Minimum number of reactions to consider the check to be met

    :returns:
        True if the total number of reactions to status is equal to or more than the reactions_threshold.
        False in any other case, including if the status does not contain any reaction counts at all.
    """
    if not (pleroma := status.get("pleroma")):
        return False

    if not (reactions := pleroma.get("emoji_reactions")):
        return False

    log.debug(f"enough_reactions_to_keep - {reactions_threshold=} - reactions={json.dumps(reactions, indent=4)}")

    total_reactions = 0
    for reaction in reactions:
        if emo_count := reaction.get("count"):
            total_reactions += emo_count

    return total_reactions >= reactions_threshold
