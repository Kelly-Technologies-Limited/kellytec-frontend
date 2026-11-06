"""Browser refresh cadence supplied by the owning application's runtime."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RefreshPolicy:
    """None means manual; an enabled interval is measured in seconds."""

    interval_seconds: int | None = None

    def __post_init__(self) -> None:
        if self.interval_seconds is not None and (
            type(self.interval_seconds) is not int or not 60 <= self.interval_seconds <= 86400
        ):
            raise ValueError("Automatic page refresh requires an interval of 60–86400 seconds")

    def as_dict(self) -> dict[str, str | int | None]:
        return {
            "mode": "manual" if self.interval_seconds is None else "interval",
            "interval_seconds": self.interval_seconds,
        }
