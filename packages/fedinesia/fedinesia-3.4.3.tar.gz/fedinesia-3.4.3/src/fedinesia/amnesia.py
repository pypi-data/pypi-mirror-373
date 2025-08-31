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
import sys
from pathlib import Path
from typing import Annotated

import msgspec
import msgspec.json
import msgspec.toml
import stamina
import typer
from loguru import logger as log
from whenever import Instant

from fedinesia import PROGRESS_ID_KEY
from fedinesia import __display_name__
from fedinesia import __version__
from fedinesia.config import setup_shop
from fedinesia.fedi import FediHelper
from fedinesia.util import AuditLog

stamina.instrumentation.set_on_retry_hooks([])


@log.catch
async def main(  # noqa:PLR0913
    config_file: str,
    is_dry_run: bool,
    audit_log_file: Path | None,
    audit_log_style: AuditLog.Style | None,
    limit: int | None,
    save_progress_path: Path | None,
    continue_from_saved_progress: bool,
) -> None:
    """Perform app function."""
    config = await setup_shop(config_file=config_file)

    oldest_to_keep = Instant.now().subtract(seconds=config.bot.delete_after).py_datetime()

    log.info(f"Welcome to {__display_name__} {__version__}")
    log.debug(f"{config=}")

    continue_max_id: str | None = None
    if continue_from_saved_progress and save_progress_path and save_progress_path.exists():
        with save_progress_path.open(mode="rb") as progress_file:
            saved_progress = msgspec.toml.decode(progress_file.read())
            continue_max_id = saved_progress.get(PROGRESS_ID_KEY)

    if audit_log_style is None:
        audit_log_style = AuditLog.Style.PLAIN

    fedi_helper = FediHelper(
        config=config,
        oldest_to_keep=oldest_to_keep,
        audit_log=AuditLog(audit_log=audit_log_file, style=audit_log_style),
    )
    await fedi_helper.connect()

    await fedi_helper.retrieve_and_filter_statuses(continue_max_id=continue_max_id, limit=limit)

    # If dry-run has been specified, print out list of statuses that would be deleted
    if is_dry_run:
        fedi_helper.delete_dry_run()

    # Dry-run has not been specified... delete statuses!
    else:
        await fedi_helper.delete_statuses(save_progress_path=save_progress_path)


def start() -> None:
    """Start app."""
    typer.run(typer_async_shim)


def typer_async_shim(  # noqa: PLR0913
    config_file: Annotated[str, typer.Option("-c", "--config-file")] = "config.json",
    audit_log_file: Annotated[
        Path | None,
        typer.Option("-a", "--audit-log-file", file_okay=True, dir_okay=False, writable=True),
    ] = None,
    audit_log_style: AuditLog.Style | None = None,
    limit: Annotated[int | None, typer.Option("-l", "--limit")] = None,
    dry_run: Annotated[bool, typer.Option("-d", "--dry-run/--no-dry-run")] = False,
    save_progress: Annotated[
        Path | None,
        typer.Option("-s", "--save-progress", file_okay=True, dir_okay=False, writable=True),
    ] = None,
    continue_from_saved_progress: Annotated[bool, typer.Option("--continue/--no-continue")] = False,
    logging_config_path: Annotated[
        Path | None,
        typer.Option(
            "--logging-config",
            help="Full Path to logging config file",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ] = None,
) -> None:
    """Delete fediverse history. For more information look at https://codeberg.org/MarvinsMastodonTools/fedinesia."""
    if logging_config_path:
        with logging_config_path.open(mode="rb") as log_config_file:
            logging_config = msgspec.toml.decode(log_config_file.read())

        for handler in logging_config.get("handlers"):
            if handler.get("sink") == "sys.stdout":
                handler["sink"] = sys.stdout

        log.configure(**logging_config)

    if continue_from_saved_progress and (not save_progress):
        raise typer.BadParameter("--continue can only be specified if --save-progress has also been specified.")

    if audit_log_style and (not audit_log_file):
        raise typer.BadParameter("--audit-log-style can only be specified if --audit-log-file has also been specified.")

    if audit_log_file and (not audit_log_style):
        audit_log_style = AuditLog.Style.PLAIN

    asyncio.run(
        main(
            config_file=config_file,
            is_dry_run=dry_run,
            audit_log_file=audit_log_file,
            audit_log_style=audit_log_style,
            limit=limit,
            save_progress_path=save_progress,
            continue_from_saved_progress=continue_from_saved_progress,
        )
    )
