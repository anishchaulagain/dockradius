"""
DockRadius Docker Command Parser.
Parses Docker CLI commands into structured ParsedCommand objects.
Static analysis only — no command execution.
"""

import logging
import shlex
from typing import Optional

from app.models.schemas import ParsedCommand

logger = logging.getLogger(__name__)

SUPPORTED_COMMANDS: list[str] = [
    "docker run",
    "docker build",
    "docker exec",
    "docker stop",
    "docker rm",
    "docker network create",
    "docker volume create",
]

ALLOWED_FLAGS: dict[str, set[str]] = {
    "run": {"-d", "--detach", "-i", "--interactive", "-t", "--tty", "-p", "--publish", "-v", "--volume", "-e", "--env", "--name", "--network", "--rm", "--entrypoint", "--workdir", "-w", "-u", "--user", "-a", "--attach"},
    "build": {"-t", "--tag", "-f", "--file", "--build-arg", "--no-cache", "--pull", "--push", "--target", "--label", "--ssh", "--secret"},
    "exec": {"-i", "--interactive", "-t", "--tty", "-d", "--detach", "-u", "--user", "-e", "--env", "-w", "--workdir", "--privileged"},
    "stop": {"-t", "--time"},
    "rm": {"-f", "--force", "-l", "--link", "-v", "--volumes"},
    "network create": {"-d", "--driver", "--gateway", "--subnet", "--ip-range", "--internal", "--attachable", "--label", "--opt"},
    "volume create": {"-d", "--driver", "--label", "--opt"},
}


def _validate_flag(cmd_type: str, flag: str):
    """Check if a flag is valid for the given command type."""
    if not flag.startswith("-"):
        return

    allowed = ALLOWED_FLAGS.get(cmd_type, set())

    # Handle long flags
    if flag.startswith("--"):
        if flag not in allowed:
            raise DockerParserError(f"Unknown flag for 'docker {cmd_type}': {flag}")
    else:
        # Check each character in a short flag cluster (e.g., -it -> -i, -t)
        for char in flag[1:]:
            short_flag = f"-{char}"
            if short_flag not in allowed:
                raise DockerParserError(f"Unknown flag for 'docker {cmd_type}': {short_flag}")



class DockerParserError(Exception):
    """Raised when a Docker command cannot be parsed."""
    pass


class UnsupportedCommandError(Exception):
    """Raised when the command is not in the supported list."""
    pass


def parse_command(raw: str) -> ParsedCommand:
    """
    Parse a Docker CLI command string into a structured ParsedCommand.

    Args:
        raw: Raw Docker CLI command string.

    Returns:
        ParsedCommand with extracted parameters.

    Raises:
        UnsupportedCommandError: If command is not supported.
        DockerParserError: If command is malformed.
    """
    raw = raw.strip()
    if not raw:
        raise DockerParserError("Empty command provided")

    try:
        tokens = shlex.split(raw)
    except ValueError as e:
        raise DockerParserError(f"Malformed command: {e}")

    if not tokens or tokens[0] != "docker":
        raise DockerParserError("Command must start with 'docker'")

    if len(tokens) < 2:
        raise DockerParserError("Incomplete Docker command")

    # Determine the base command (handle two-word commands like 'network create')
    sub_command = tokens[1]
    base_command: str
    arg_start: int

    if sub_command in ("network", "volume") and len(tokens) >= 3 and tokens[2] == "create":
        base_command = f"{sub_command} create"
        arg_start = 3
    else:
        base_command = sub_command
        arg_start = 2

    full_command = f"docker {base_command}"
    if full_command not in SUPPORTED_COMMANDS:
        raise UnsupportedCommandError(f"Unsupported command: {full_command}")

    # Parse remaining tokens based on command type
    remaining = tokens[arg_start:]

    if base_command == "run":
        return _parse_run(remaining, raw)
    elif base_command == "build":
        return _parse_build(remaining, raw)
    elif base_command == "exec":
        return _parse_exec(remaining, raw)
    elif base_command in ("stop", "rm"):
        return _parse_simple(base_command, remaining, raw)
    elif base_command == "network create":
        return _parse_network_create(remaining, raw)
    elif base_command == "volume create":
        return _parse_volume_create(remaining, raw)
    else:
        raise UnsupportedCommandError(f"Unsupported: {full_command}")


def _parse_run(tokens: list[str], raw: str) -> ParsedCommand:
    """Parse 'docker run' arguments."""
    ports: list[str] = []
    volumes: list[str] = []
    environment: list[str] = []
    network: Optional[str] = None
    container_name: Optional[str] = None
    flags: list[str] = []
    image: Optional[str] = None
    extra_args: list[str] = []

    i = 0
    while i < len(tokens):
        tok = tokens[i]

        if tok.startswith("-"):
            _validate_flag("run", tok)

        if tok in ("-p", "--publish") and i + 1 < len(tokens):
            ports.append(tokens[i + 1])
            i += 2
        elif tok in ("-v", "--volume") and i + 1 < len(tokens):
            volumes.append(tokens[i + 1])
            i += 2
        elif tok in ("-e", "--env") and i + 1 < len(tokens):
            environment.append(tokens[i + 1])
            i += 2
        elif tok == "--network" and i + 1 < len(tokens):
            network = tokens[i + 1]
            i += 2
        elif tok == "--name" and i + 1 < len(tokens):
            container_name = tokens[i + 1]
            i += 2
        elif tok.startswith("-"):
            flags.append(tok)
            i += 1
        elif image is None:
            image = tok
            i += 1
        else:
            extra_args.append(tok)
            i += 1

    return ParsedCommand(
        base_command="run",
        image=image,
        container_name=container_name,
        ports=ports,
        volumes=volumes,
        network=network,
        environment=environment,
        flags=flags,
        extra_args=extra_args,
        raw_command=raw,
    )


def _parse_build(tokens: list[str], raw: str) -> ParsedCommand:
    """Parse 'docker build' arguments."""
    flags: list[str] = []
    image: Optional[str] = None
    extra_args: list[str] = []

    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.startswith("-"):
            _validate_flag("build", tok)
        if tok in ("-t", "--tag") and i + 1 < len(tokens):
            image = tokens[i + 1]
            i += 2
        elif tok in ("-f", "--file") and i + 1 < len(tokens):
            flags.append(f"-f {tokens[i + 1]}")
            i += 2
        elif tok.startswith("-"):
            flags.append(tok)
            i += 1
        else:
            extra_args.append(tok)
            i += 1

    return ParsedCommand(
        base_command="build",
        image=image,
        flags=flags,
        extra_args=extra_args,
        raw_command=raw,
    )


def _parse_exec(tokens: list[str], raw: str) -> ParsedCommand:
    """Parse 'docker exec' arguments."""
    flags: list[str] = []
    container_name: Optional[str] = None
    extra_args: list[str] = []

    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.startswith("-"):
            _validate_flag("exec", tok)
        if tok.startswith("-"):
            flags.append(tok)
            i += 1
        elif container_name is None:
            container_name = tok
            i += 1
        else:
            extra_args.append(tok)
            i += 1

    return ParsedCommand(
        base_command="exec",
        container_name=container_name,
        flags=flags,
        extra_args=extra_args,
        raw_command=raw,
    )


def _parse_simple(base_cmd: str, tokens: list[str], raw: str) -> ParsedCommand:
    """Parse 'docker stop' or 'docker rm' arguments."""
    flags: list[str] = []
    container_name: Optional[str] = None
    extra_args: list[str] = []

    for tok in tokens:
        if tok.startswith("-"):
            _validate_flag(base_cmd, tok)
            flags.append(tok)
        elif container_name is None:
            container_name = tok
        else:
            extra_args.append(tok)

    return ParsedCommand(
        base_command=base_cmd,
        container_name=container_name,
        flags=flags,
        extra_args=extra_args,
        raw_command=raw,
    )


def _parse_network_create(tokens: list[str], raw: str) -> ParsedCommand:
    """Parse 'docker network create' arguments."""
    flags: list[str] = []
    network: Optional[str] = None

    for tok in tokens:
        if tok.startswith("-"):
            _validate_flag("network create", tok)
            flags.append(tok)
        elif network is None:
            network = tok

    return ParsedCommand(
        base_command="network create",
        network=network,
        flags=flags,
        raw_command=raw,
    )


def _parse_volume_create(tokens: list[str], raw: str) -> ParsedCommand:
    """Parse 'docker volume create' arguments."""
    flags: list[str] = []
    extra_args: list[str] = []
    volume_name: Optional[str] = None

    for tok in tokens:
        if tok.startswith("-"):
            _validate_flag("volume create", tok)
            flags.append(tok)
        elif volume_name is None:
            volume_name = tok

    volumes = [volume_name] if volume_name else []

    return ParsedCommand(
        base_command="volume create",
        volumes=volumes,
        flags=flags,
        raw_command=raw,
    )
