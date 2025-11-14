from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class PipelineStatus:
    running: bool = False
    step: Optional[str] = None
    progress: int = 0
    error: Optional[str] = None

    def to_dict(self):
        return asdict(self)


# global instance
pipeline_status = PipelineStatus()


def update_status(step: str, progress: int):
    pipeline_status.running = True
    pipeline_status.step = step
    pipeline_status.progress = progress  # 0–100
    pipeline_status.error = None
