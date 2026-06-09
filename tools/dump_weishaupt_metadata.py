"""Read-only helper to dump Weishaupt web metadata files.

The script performs only HTTP GET requests. It never sends CanApiJson SET
commands and never prints credentials.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPBasicAuthHandler, HTTPPasswordMgrWithDefaultRealm
from urllib.request import build_opener


PATHS = (
    "/script/einstellung.js",
    "/script/Form_eth_log.js",
    "/sd/systable.csv",
)


def build_arg_parser() -> argparse.ArgumentParser:
    """Build the command line parser."""
    parser = argparse.ArgumentParser(
        description="Dump read-only Weishaupt metadata files for inspection."
    )
    parser.add_argument("--host", required=True, help="Weishaupt SG host or IP")
    parser.add_argument(
        "--username",
        default=os.environ.get("WEISHAUPT_USERNAME", "admin"),
        help="HTTP username; defaults to WEISHAUPT_USERNAME or admin",
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("WEISHAUPT_PASSWORD"),
        help="HTTP password; defaults to WEISHAUPT_PASSWORD",
    )
    parser.add_argument(
        "--output-dir",
        default="weishaupt_metadata",
        help="Directory where downloaded files are written",
    )
    return parser


def opener_for(base_url: str, username: str, password: str | None):
    """Create an opener with optional Basic Auth."""
    if not password:
        return build_opener()

    password_mgr = HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, base_url, username, password)
    return build_opener(HTTPBasicAuthHandler(password_mgr))


def safe_name(path: str) -> str:
    """Convert a URL path to a filesystem-safe file name."""
    return path.strip("/").replace("/", "__")


def main() -> int:
    """Run the read-only metadata dump."""
    args = build_arg_parser().parse_args()
    host = args.host.removeprefix("http://").removeprefix("https://").strip("/")
    base_url = f"http://{host}"
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    opener = opener_for(base_url, args.username, args.password)

    for path in PATHS:
        url = f"{base_url}{path}"
        target = output_dir / safe_name(path)
        try:
            with opener.open(url, timeout=15) as response:
                target.write_bytes(response.read())
        except (HTTPError, URLError, TimeoutError) as err:
            print(f"{path}: failed ({err})")
            continue
        print(f"{path}: wrote {target}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
