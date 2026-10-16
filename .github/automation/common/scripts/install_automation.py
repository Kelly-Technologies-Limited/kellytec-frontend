"""Bootstrap the accepted Automation wheel without importing Automation or floating source."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from email.parser import BytesParser
from pathlib import Path


def run(*args: str) -> bytes:
    """Run a bounded argument vector, keeping credentials in the environment."""
    result = subprocess.run(args, capture_output=True, timeout=600, check=False)
    if result.returncode:
        raise RuntimeError(f"{args[0]} failed: {result.stderr.decode(errors='replace')[-3000:]}")
    return result.stdout


def initial_lock(declaration: dict, version: str) -> dict:
    """Allow the explicitly requested first release only for dependency-update bootstrap."""
    if version != declaration["initial_version"] or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Initial tool installation requires the declared first release version")
    repository = declaration["source_repository"]
    tag = declaration["tag_prefix"] + version
    release = json.loads(run("gh", "api", f"repos/{repository}/releases/tags/{tag}"))
    if release["draft"] or release["prerelease"] or release.get("immutable") is not True:
        raise ValueError("Initial Automation release must be formally published and immutable")
    assets = [asset for asset in release["assets"] if asset["name"] == "release.json"]
    if len(assets) != 1 or assets[0]["size"] > 1024 * 1024:
        raise ValueError("Initial Automation release requires one bounded manifest")
    manifest = json.loads(
        run(
            "gh",
            "api",
            f"repos/{repository}/releases/assets/{assets[0]['id']}",
            "-H",
            "Accept: application/octet-stream",
        )
    )
    if (
        manifest["schema_version"] != 1
        or manifest["product"] != "kellytec-automation"
        or manifest["version"] != version
        or manifest["source"]["repository"] != repository
    ):
        raise ValueError("Initial release differs from the configured Automation publisher")
    commit = json.loads(run("gh", "api", f"repos/{repository}/commits/{tag}"))["sha"]
    if manifest["source"]["commit"] != commit:
        raise ValueError("Initial release tag differs from its source")
    registry = declaration["install"]["index"].removesuffix("simple/")
    if any(
        artifact["registry"] != registry or artifact["distribution"] != "kellytec-automation"
        for artifact in manifest["artifacts"]
    ):
        raise ValueError("Initial release package location differs from the configured index")
    return {
        "version": version,
        "commit": commit,
        "artifacts": {
            a["filename"]: a["sha256"]
            for a in manifest["artifacts"]
            if a["filename"].endswith(".whl")
        },
    }


def install(root: Path, *, bootstrap_version: str | None = None) -> dict:
    """Install the repository lock; missing locks fail outside explicit first-upgrade bootstrap."""
    configuration = json.loads(
        (root / ".github/automation/common/dependencies/products.json").read_text(encoding="utf-8")
    )
    declaration = configuration["tools"]["automation"]
    path = (root / declaration["lock"]).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Automation lock escapes the repository")
    if path.is_file():
        lock = json.loads(path.read_text(encoding="utf-8"))
    elif bootstrap_version is not None:
        lock = initial_lock(declaration, bootstrap_version)
    else:
        raise ValueError(
            "Automation lock is missing. Publish the first Automation release and merge its initialization PR."
        )
    if not re.fullmatch(r"\d+\.\d+\.\d+", lock["version"]) or not re.fullmatch(
        r"[0-9a-f]{40}", lock["commit"]
    ):
        raise ValueError("Invalid Automation release identity")
    hashes = lock["artifacts"]
    if not hashes or any(
        not re.fullmatch(r"[A-Za-z0-9_.+-]+\.whl", name)
        or not re.fullmatch(r"[0-9a-f]{64}", digest)
        for name, digest in hashes.items()
    ):
        raise ValueError("Automation lock requires exact wheel filenames and hashes")
    index = declaration["install"]["index"]
    if not re.fullmatch(
        r"https://[a-z0-9-]+-python\.pkg\.dev/[a-z0-9-]+/[a-z0-9-]+/simple/", index
    ):
        raise ValueError("Automation requires an explicit private Python package index")
    destination = root / ".automation/dependencies/automation"
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination) as temporary:
        staging = Path(temporary)
        requirement = staging / "requirement.txt"
        requirement.write_text(
            f"kellytec-automation=={lock['version']} "
            + " ".join(f"--hash=sha256:{digest}" for digest in hashes.values())
            + "\n",
            encoding="utf-8",
        )
        run(
            sys.executable,
            "-m",
            "pip",
            "download",
            "--no-deps",
            "--only-binary=:all:",
            "--keyring-provider",
            "import",
            "--index-url",
            index,
            "--require-hashes",
            "-r",
            str(requirement),
            "--dest",
            str(staging),
        )
        wheels = list(staging.glob("*.whl"))
        if len(wheels) != 1 or hashlib.sha256(wheels[0].read_bytes()).hexdigest() != hashes.get(
            wheels[0].name
        ):
            raise ValueError("Downloaded Automation wheel differs from its lock")
        with zipfile.ZipFile(wheels[0]) as archive:
            names = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
            if len(names) != 1:
                raise ValueError("Automation wheel requires one metadata document")
            metadata = BytesParser().parsebytes(archive.read(names[0]))
        if (
            metadata["Name"].replace("_", "-") != "kellytec-automation"
            or metadata["Version"] != lock["version"]
        ):
            raise ValueError("Automation wheel metadata differs from its lock")
        wheel = destination / wheels[0].name
        wheel.write_bytes(wheels[0].read_bytes())
        run(sys.executable, "-m", "pip", "install", "--force-reinstall", str(wheel))
    if os.environ.get("GITHUB_OUTPUT"):
        with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as output:
            output.write(f"sha={lock['commit']}\nversion={lock['version']}\n")
    return lock


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap-version")
    args = parser.parse_args()
    install(Path.cwd(), bootstrap_version=args.bootstrap_version)
