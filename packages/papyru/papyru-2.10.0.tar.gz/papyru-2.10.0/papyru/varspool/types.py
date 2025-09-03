from dataclasses import dataclass
from datetime import datetime
from typing import List


class JobException(Exception):
    pass


class FetchJobException(JobException):
    pass


class SaveJobException(JobException):
    pass


class StatusConflict(SaveJobException):
    def __init__(self, job):
        self.job = job
        super().__init__('invalid previous status')


@dataclass
class JobStatusHistoryItem:
    status: str
    checksum: str
    date: datetime
    data: dict

    @staticmethod
    def from_dict(entry_dict: dict):
        return JobStatusHistoryItem(
            status=entry_dict['status'],
            checksum=entry_dict['checksum'],
            date=datetime.fromisoformat(entry_dict['date']),
            data=entry_dict['data'])

    def to_dict(self):
        return {
            'status': self.status,
            'checksum': self.checksum,
            'date': self.date.isoformat(),
            'data': self.data,
        }


@dataclass
class JobStatusHistory:
    location: str
    items: List[JobStatusHistoryItem]

    @staticmethod
    def from_dict(history_dict: dict):
        return JobStatusHistory(location=history_dict['location'],
                                items=list(map(JobStatusHistoryItem.from_dict,
                                               history_dict['items'])))

    def to_dict(self):
        return {
            'location': self.location,
            'items': list(map(lambda it: it.to_dict(),
                              self.items)),
        }


@dataclass
class Job:
    id: int
    location: str
    status_history: JobStatusHistory

    @staticmethod
    def from_dict(job_dict: dict):
        return Job(id=job_dict['id'],
                   location=job_dict['location'],
                   status_history=JobStatusHistory.from_dict(
                       job_dict['status_history']))

    def to_dict(self):
        return {
            'id': self.id,
            'location': self.location,
            'status_history': self.status_history.to_dict(),
        }

    def get_status_data(self, status: str) -> dict:
        status_list = list(filter(lambda i: i.status == status,
                                  self.status_history.items))
        if len(status_list) != 1:
            raise JobException('%d status history items found with status `%s`'
                               % (len(status_list), status))

        return status_list[0].data
