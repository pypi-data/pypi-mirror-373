import logging
from pathlib import Path

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class OpenEOExecutorParameters(BaseModel):
    """Pydantic model of parameters required to run openeo job."""

    process_graph: dict
    user_workspace: Path

    @property
    def root_path(self) -> Path:
        return self.get_root_path(self.user_workspace)

    @staticmethod
    def get_root_path(user_workspace):
        return user_workspace / "OPENEO"

    @property
    def results_path(self) -> Path:
        return self.get_results_path(self.user_workspace)

    @classmethod
    def get_results_path(cls, user_workspace) -> Path:
        return cls.get_root_path(user_workspace) / "results"

    @property
    def stac_path(self) -> Path:
        return self.results_path / "STAC"

    @property
    def stac_items_path(self) -> Path:
        return self.stac_path / "items"
