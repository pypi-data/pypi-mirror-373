import json
import logging
from enum import Enum
from pathlib import Path
from typing import Any

import json5
from pydantic import BaseModel, Field
from util_common.path import sort_paths

from workspace_services.batch import Batch, batch_service
from workspace_services.settings import workspace_settings


class TaskType(str, Enum):
    CLASSIFICATION = "classification"


class WorkspaceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class Workspace(BaseModel):
    id: str
    description: str = Field(default="")
    task_description: str = Field(default="")
    task_id: str = Field(default="page_classification")
    task_type: TaskType
    tag_config: dict[str, Any] = Field(default_factory=dict)
    batches: list[str] = Field(default_factory=list)
    status: WorkspaceStatus = Field(default=WorkspaceStatus.ACTIVE)


class WorkspaceService:
    def __init__(self):
        self.workspace_root = workspace_settings.workspace_root
        self.task_root = workspace_settings.task_root
        self.batch_root = workspace_settings.batch_root
        self.workspaces: dict[str, Workspace] = dict()

    def get_task_settings(self, task_id: str) -> dict[str, Any]:
        task_settings_path = self.task_root / f"{task_id}.jsonc"
        if not task_settings_path.exists():
            raise ValueError(f"Task settings {task_settings_path} not found")
        task_settings = json5.loads(task_settings_path.read_text(encoding="utf-8"))
        if not isinstance(task_settings, dict):
            raise ValueError(f"Invalid task settings: {task_settings_path}")
        if not (isinstance(task_settings['task_type'], str) and task_settings['task_type']):
            raise ValueError(f"Invalid task type: {task_settings_path}")
        return task_settings

    def get_workspace_settings(self, workspace_id: str) -> dict[str, Any]:
        workspace_settings_path = self.workspace_root / f"{workspace_id}.jsonc"
        if not workspace_settings_path.exists():
            raise ValueError(f"Workspace config {workspace_settings_path} not found")
        try:
            workspace_settings = json5.loads(workspace_settings_path.read_text(encoding="utf-8"))
        except Exception as e:
            raise ValueError(f"Failed to load workspace settings {workspace_settings_path}: {e}")
        if not isinstance(workspace_settings, dict):
            raise ValueError(f"Invalid workspace settings: {workspace_settings_path}")
        return workspace_settings

    def get_workspace(self, workspace_id: str) -> Workspace:
        workspace_settings = self.get_workspace_settings(workspace_id)

        # 处理 task_id 字段：如果 task_id 不存在，则使用默认值 'page_classification'
        task_id = workspace_settings.get('task_id') or 'page_classification'
        try:
            task_settings = self.get_task_settings(task_id)
        except Exception as e:
            logging.warning(f"Failed to load task settings {task_id}: {e}")
            task_id = 'page_classification'
            task_settings = self.get_task_settings(task_id)

        # 处理 batches 字段：如果是字典列表，提取 id 字段
        batches_data = workspace_settings.get('batches', [])
        if batches_data and isinstance(batches_data[0], dict):
            batches = [
                batch['id'] for batch in batches_data if isinstance(batch, dict) and 'id' in batch
            ]
        else:
            batches = batches_data

        return Workspace(
            id=workspace_id,
            description=workspace_settings.get('description', ''),
            task_description=task_settings.get('description', ''),
            task_id=task_id,
            task_type=TaskType(task_settings['task_type']),
            tag_config=task_settings.get('tag_config', {}),
            batches=batches,
            status=WorkspaceStatus.ACTIVE,
        )

    def load_workspaces(self) -> dict[str, Workspace]:
        """
        加载所有 workspace 配置, 并缓存到 self.workspaces 中。
        用户刷新 /ui/workspaces 页面时, 重新加载所有 workspace 配置。
        """
        for settings_path in sort_paths(self.workspace_root.glob('*.jsonc')):
            workspace_id = settings_path.stem
            try:
                self.workspaces[workspace_id] = self.get_workspace(workspace_id)
            except Exception as e:
                logging.warning(f"Failed to load workspace {workspace_id}: {e}")
        return self.workspaces

    def get_workspace_batches(self, workspace_id: str) -> list[Batch]:
        if workspace_id not in self.workspaces:
            raise ValueError(f"Workspace {workspace_id} not found")
        batches = []
        for batch_id in sort_paths(self.workspaces[workspace_id].batches):
            batches.append(batch_service.get_batch(str(batch_id)))
        return batches

    def get_tag_path(self, workspace_id: str, page_dir: Path) -> Path:
        """
        tag 文件路径: 对应的 page 目录下, 文件名: tag-<tag_name>.json
        """
        if not page_dir.exists():
            raise ValueError(f"Page directory {page_dir} not found")

        workspace = self.get_workspace(workspace_id)
        if workspace and workspace.tag_config and workspace.tag_config.get("tag_name"):
            tag_name = workspace.tag_config["tag_name"]
            return page_dir / f"tag-{tag_name}.json"
        raise ValueError(f"Tag name not found for workspace {workspace_id}")

    def get_tag(self, workspace_id: str, page_dir: Path) -> dict | list[dict]:
        tag_path = self.get_tag_path(workspace_id, page_dir)
        if not tag_path.exists():
            return {}

        tag_data = json.loads(tag_path.read_text(encoding="utf-8"))
        return tag_data

    def save_tag(self, workspace_id: str, page_dir: Path, tag_data: dict | list[dict]) -> bool:
        tag_path = self.get_tag_path(workspace_id, page_dir)
        tag_path.write_text(json.dumps(tag_data, ensure_ascii=False, indent=2), encoding="utf-8")
        return True


workspace_service = WorkspaceService()
