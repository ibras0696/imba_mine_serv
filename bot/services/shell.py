from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Tuple


async def run(
    command: str,
    workdir: str | Path | None = None,
    dry_run: bool = False,
) -> Tuple[int, str, str]:
    if dry_run:
        logging.info("[DRY-RUN] %s", command)
        return 0, command, ""

    process = await asyncio.create_subprocess_shell(
        command,
        cwd=str(workdir) if workdir else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout_bytes, stderr_bytes = await process.communicate()
    stdout = stdout_bytes.decode(errors="replace").strip()
    stderr = stderr_bytes.decode(errors="replace").strip()
    return process.returncode, stdout, stderr
