import logging
import subprocess
from collections.abc import Sequence

from external_resources_io.config import Config

logger = logging.getLogger(__name__)


def terraform_available() -> bool:
    try:
        subprocess.run(["terraform", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def terraform_fmt(data: str) -> str:
    if not terraform_available():
        return data
    return subprocess.run(
        ["terraform", "fmt", "-"],
        input=data,
        text=True,
        check=True,
        capture_output=True,
    ).stdout


def terraform_run(args: Sequence[str], *, dry_run: bool | None = None) -> str:
    """Run a terraform command."""
    config = Config()
    args = [*config.terraform_cmd.split(), *args]
    dry_run = dry_run if dry_run is not None else config.dry_run
    if dry_run:
        logger.debug(f"cmd: {' '.join(args)}")
        return ""

    try:
        cmd = subprocess.run(args, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.exception(e.stdout)
        logger.exception(e.stderr)
        raise
    return cmd.stdout
