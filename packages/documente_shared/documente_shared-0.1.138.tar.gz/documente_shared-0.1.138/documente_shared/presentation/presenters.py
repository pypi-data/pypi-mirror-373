from dataclasses import dataclass

from documente_shared.application.dates import utc_now
from documente_shared.domain.enums.common import TaskResultStatus


@dataclass
class TaskResultPresenter(object):
    status: TaskResultStatus = TaskResultStatus.SUCCESS

    @property
    def to_dict(self) -> dict:
        return {
            "status": str(self.status),
            "completed_at": utc_now().isoformat(),
        }