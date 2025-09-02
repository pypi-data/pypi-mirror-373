from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from batch_store import batch_store_settings


class WorkspaceSettings(BaseSettings):

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="allow",
    )

    @property
    def data_root(self) -> Path:
        return batch_store_settings.data_root

    @property
    def batch_root(self) -> Path:
        return self.data_root.joinpath("batches")

    @property
    def task_root(self) -> Path:
        return self.data_root.joinpath("tasks")

    @property
    def workspace_root(self) -> Path:
        return self.data_root.joinpath("workspaces")


workspace_settings = WorkspaceSettings()
