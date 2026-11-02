"""One content panel corresponding to an enabled Tab."""

from dataclasses import dataclass

@dataclass(frozen=True)
class TabPanel:
    view: str

    def __post_init__(self) -> None:
        if not (bool(self.view) and self.view.replace("-", "").isalnum()):
            raise ValueError("panel view is invalid")
