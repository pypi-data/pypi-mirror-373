from pathlib import Path

from pydantic import BaseModel, Field
from util_common.path import sort_paths

from batch_store import BatchStore, Sample
from workspace_services.memory_manager import cache_manager
from workspace_services.settings import workspace_settings


class Batch(BaseModel):
    id: str
    description: str = Field(default="")
    batch_dir: Path


class BatchService:
    def __init__(self):
        self.batch_root = workspace_settings.batch_root
        self.batches: dict[str, Batch] = self._load_batches()

    def _load_batches(self) -> dict[str, Batch]:
        batches: dict[str, Batch] = dict()
        for batch_dir in sort_paths(self.batch_root.iterdir()):
            if batch_dir.is_dir():
                batches[batch_dir.name] = Batch(id=batch_dir.name, batch_dir=batch_dir)
                if batch_dir.joinpath('readme.md').exists():
                    batches[batch_dir.name].description = (
                        batch_dir.joinpath('readme.md').read_text(encoding='utf-8').strip()
                    )
        return batches

    def get_batch(self, batch_id: str) -> Batch:
        if batch_id not in self.batches:
            raise ValueError(f"Batch {batch_id} not found")
        return self.batches[batch_id]

    def get_batch_samples(self, batch_id: str) -> list[Sample]:
        # 尝试从缓存获取
        cache_key = f"batch_samples_{batch_id}"
        cached_samples = cache_manager.get(cache_key)
        if cached_samples is not None:
            return cached_samples

        batch_store = BatchStore(batch_id)
        if not batch_store.unified_dir.is_dir():
            raise ValueError(f"Batch {batch_id} not found")

        samples = batch_store.load_unified_samples()
        cache_manager.set(cache_key, samples)
        return samples


batch_service = BatchService()
