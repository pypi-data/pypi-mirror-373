import os
import subprocess
import tempfile
from pathlib import Path

import gnupg
from rich import print
from rich.table import Table

from arkindex_cli.auth import Profiles
from arkindex_cli.utils import ask


def add_secrets_parser(subcommands) -> None:
    parser = subcommands.add_parser(
        "secrets",
        help="Manage local Ponos Secrets to replace those from an Arkindex instance.",
        description="Manage local Ponos Secrets to replace those from an Arkindex instance.",
    )
    parser.add_argument(
        "name",
        type=str,
        help="The name of the secret to manage locally",
    )
    parser.set_defaults(func=run)


def select_gpg_key(gpg):
    # List gpg keys as a table
    table = Table(show_header=True)
    table.add_column("Key ID")
    table.add_column("User")
    keys = []
    for key in gpg.list_keys(True):
        table.add_row(key["keyid"], "\n".join(key["uids"]))
        keys.append(key["keyid"])
    print(table)

    # Ask user to select a key
    selected = None
    while selected not in keys:
        selected = ask("Please select a Key ID to encrypt secrets")

    return selected


def run(
    name: str,
    profile_slug: str | None = None,
    gitlab_secure_file: Path | None = None,
) -> int:
    print(f"[blue]Editing secret {name}")

    # Build path
    profiles = Profiles()
    secrets_dir = profiles.dir / "secrets"
    if not secrets_dir.exists():
        secrets_dir.mkdir(parents=True, mode=0o700)
    path = secrets_dir / name

    # Setup GPG client
    gpg = gnupg.GPG()

    if profiles.gpg_key is None:
        profiles.gpg_key = select_gpg_key(gpg)
        profiles.save()

    # Decrypt initial content
    content = None
    if path.exists():
        try:
            decrypted = gpg.decrypt(path.read_bytes())
            content = decrypted.data
        except Exception as e:
            print(f"[red]Failed to decrypt secret {path}: {e}")
            return 1

    # Open editor
    editor = os.environ.get("EDITOR", "vim")
    with tempfile.NamedTemporaryFile(suffix=".ark") as f:
        if content is not None:
            f.write(content)
            f.flush()

        subprocess.call([editor, f.name])

        f.seek(0)
        content = f.read()

    # Encrypt final content
    encrypted = gpg.encrypt(content, [profiles.gpg_key])
    assert encrypted.ok, f"Encryption failed: {encrypted.status}"
    if not path.parent.exists():
        path.parent.mkdir(parents=True, mode=0o700)

    path.write_bytes(encrypted.data)
