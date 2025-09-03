from http import HTTPStatus
from os import environ, getpid
from typing import List, Optional
from urllib.parse import urljoin

import requests

from papyru.utils import log

from .serializers import JobSerializer, JobStatusHistorySerializer
from .types import FetchJobException, Job, SaveJobException, StatusConflict


def _debug_info() -> dict:
    return {
        'pod': environ.get('HOSTNAME', 'could not determine pod.'),
        'pid': getpid(),
    }


def fetch_jobs(queue_url: str, status: str, limit: Optional[int] = None
               ) -> List[Job]:
    url = urljoin(
        '%s/' % queue_url,
        'jobs?current_status=%s%s' % (
            status, ('&limit=%d' % limit if limit else '')))
    try:
        resp = requests.get(url)
    except Exception as exc:
        raise FetchJobException('%s: %s: %s' % (url, type(exc).__name__,
                                                str(exc)))
    if resp.status_code != HTTPStatus.OK:
        raise FetchJobException('%s[%d]: %s' %
                                (url, resp.status_code, resp.text))

    return list(map(lambda j: JobSerializer(representation=j).instance,
                    resp.json()['jobs']))


def create_job(queue_url, data: dict) -> Job:
    try:
        url = urljoin('%s/' % queue_url, 'jobs')
        resp = requests.post(url, json={'data': {**_debug_info(), **data}})
        if resp.status_code != HTTPStatus.CREATED:
            raise SaveJobException('%s[%d]: %s' %
                                   (url, resp.status_code, resp.text))
        if not resp.headers.get('location'):
            raise SaveJobException('%s[%d]: missing `location` header' %
                                   (url, resp.status_code))

        return JobSerializer(representation=resp.json()).instance

    except SaveJobException:
        raise

    except Exception as exc:
        raise SaveJobException(str(exc))


def add_status(job: Job, status: str, data: dict = {}, allowed_retries=3
               ) -> Job:
    def _to_job(body: dict):
        try:
            job.status_history = JobStatusHistorySerializer(
                representation=body).instance
        except Exception as exc:
            raise SaveJobException(str(exc))

        return job

    previous_status = job.status_history.items[-1]
    body = {
      'previous_status': {
        'checksum': previous_status.checksum
      },
      'status': status,
      'data': {
        **_debug_info(),
        **data,
      }
    }

    try:
        resp = requests.post(job.status_history.location, json=body)

        if resp.status_code == HTTPStatus.CONFLICT:
            raise StatusConflict(_to_job(resp.json()))

        if resp.status_code != HTTPStatus.OK:
            raise SaveJobException('%s[%d]: %s' %
                                   (job.status_history.location,
                                    resp.status_code,
                                    resp.text))

        return _to_job(resp.json())

    except SaveJobException:
        raise

    except Exception as ex:
        if allowed_retries > 0:
            log('need to retry job `%d` status update to `%s`' % (job.id,
                                                                  status))
            return add_status(job, status, data, allowed_retries - 1)

        raise SaveJobException('%s: %s' % (type(ex).__name__, str(ex)))
