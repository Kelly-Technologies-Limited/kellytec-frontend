"""Record the actual Pages deployment URL and qualified source identity."""

from pathlib import Path

from kellytec_automation.common.io.library.local_files import write_json


def record_pages_result(root: Path, snapshot: dict, url: str) -> None:
    """Retain a successful Pages result only after the platform reports its URL."""
    if not url.startswith("https://"):
        raise ValueError("Pages did not return a successful HTTPS deployment URL")
    write_json(
        root / ".automation/kellytec-website/deployment.json",
        {
            "snapshot_id": snapshot["snapshot_id"],
            "source_sha": snapshot["source_sha"],
            "target": "github-pages",
            "status": "succeeded",
            "url": url,
        },
    )
