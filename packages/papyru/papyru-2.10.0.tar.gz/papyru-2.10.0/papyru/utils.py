import logging
import re
from contextlib import contextmanager
from datetime import datetime
from enum import Enum, unique
from functools import partial, wraps
from os import getpid
from time import sleep
from typing import Dict, List, Union
from unittest.mock import patch
from uuid import uuid4

from django.db.models import QuerySet

from papyru.logger import log_info

_logger = logging.getLogger(__name__)

PYTHON_REQUESTS_DEFAULT_TIMEOUT_SECONDS = 300


@unique
class PAPEnum(Enum):
    def __str__(self):
        return self.value

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


@contextmanager
def limited_runtime(timeout):
    '''
    Checks if runtime is left.

    Example:

        .. code-block:: python

            with limited_runtime(
                    datetime.timedelta(minutes=MAX_RUNTIME_MINUTES)
            ) as has_runtime_left:
                while has_runtime_left():
                    do_something()
                    sleep(1)
    '''

    start_time = datetime.now()

    def has_runtime_left():
        return (datetime.now() - start_time) < timeout

    try:
        yield has_runtime_left
    finally:
        pass


def parse_bool(value):
    if isinstance(value, bool):
        return value
    elif value is None:
        return False
    elif isinstance(value, str):
        return value.lower() in ('true', '1', 'yes')
    elif isinstance(value, int):
        return value == 1
    elif isinstance(value, float):
        return int(value) == 1
    else:
        raise TypeError('cannot parse bool from "%s".' % value)


def setup_request_ids(ignored_domains=[]):
    '''
    Adds an additional header `pap-request-id` to Python-Requests to identify
    requests across multiple services.
    '''

    if setup_request_ids._already_patched:
        return
    else:
        setup_request_ids._already_patched = True

    import requests

    ignore_patterns = set(map(
        lambda d: re.compile('^https?://%s($|[/?])' % re.escape(d)),
        ignored_domains))

    class PatchedSession(requests.sessions.Session):
        def prepare_request(self, request):
            if any(map(lambda p: p.match(request.url),
                       ignore_patterns)):
                return super().prepare_request(request)

            request.headers = {**(request.headers or {}),
                               'pap-request-id': str(uuid4())}

            log_info('sending request %s: %s %s' % (
                request.headers.get('pap-request-id'),
                request.method,
                request.url))

            return super().prepare_request(request)

    requests.sessions.Session = PatchedSession


setup_request_ids._already_patched = False


def setup_request_default_timeout():
    '''
    Adds a default timeout in seconds to Python-Requests.
    '''

    import requests

    class PatchedSession(requests.sessions.Session):
        def send(self, request, **kwargs):
            if kwargs.get('timeout') is None:
                kwargs['timeout'] = PYTHON_REQUESTS_DEFAULT_TIMEOUT_SECONDS

            return super().send(request, **kwargs)

    requests.sessions.Session = PatchedSession


setup_request_default_timeout()


def setup_request_default_auth_tokens(url_token_mapping: Dict[str, str]):
    '''
    Adds a default Bearer Authentification Header for matching urls. Example
    `url_token_mapping`:
        .. code-block:: python
        {
            '^https?://example.org/auth': 'TOKEN',
            '^https://example.org/other_auth$': 'OTHER_TOKEN',
        }
    '''

    if setup_request_default_auth_tokens._already_patched:
        return
    else:
        setup_request_default_auth_tokens._already_patched = True

    import requests

    class PatchedSession(requests.sessions.Session):
        def prepare_request(self, request):
            _, token = next(filter(lambda m: re.search(m[0], request.url),
                            url_token_mapping.items()), (None, None))
            if token and request.headers.get('Authorization') is None:
                request.headers['Authorization'] = 'Bearer %s' % token

            return super().prepare_request(request)

    requests.sessions.Session = PatchedSession


setup_request_default_auth_tokens._already_patched = False


def silent_log_commit(self, item):
    pass


def make_silent_testcase(TestCaseClass):
    class Impl(TestCaseClass):
        @patch('papyru.logger_stdout.StdoutSink.commit', silent_log_commit)
        def run(self, *args, **kwargs):
            logger = logging.getLogger()
            _loglevel = logger.getEffectiveLevel()

            try:
                logger.setLevel(logging.CRITICAL + 1)

                result = super().run(*args, **kwargs)

                logger.setLevel(_loglevel)

                return result

            finally:
                logger.setLevel(_loglevel)
    return Impl


def log(message, level='info'):
    getattr(_logger, level)('[%d]: %s' % (getpid(), message))


# timeout in seconds
def timed_retry(num_retries=3, timeout=0.1, exception_types=[Exception]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for round in range(0, num_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    if len(list(filter(partial(isinstance, exc),
                                       exception_types))) > 0:
                        log(
                            'need to retry operation: %s: %s\nwaiting %s '
                            'seconds.'
                            % (type(exc).__name__, exc, timeout),
                            'warning')
                        sleep(timeout)
                    else:
                        raise

            return func(*args, **kwargs)
        return wrapper
    return decorator


def delete_in_chunks(query: QuerySet,
                     chunk_size: int = 1024,
                     chunks_to_delete: int = 512):
    chunks_to_delete -= 1
    affected_rows, _ = (
        query.model
        .objects
        .filter(pk__in=list(
            query.only('pk').values_list('pk', flat=True)[:chunk_size]))
        .delete())

    if affected_rows > 0 and chunks_to_delete > 0:
        return delete_in_chunks(query, chunk_size, chunks_to_delete)


def cursor_to_dict(cursor) -> List[Dict[str, Union[str, int]]]:
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def read_as_dict(list_string: str,
                 list_separator: str,
                 key_value_separator: str):
    return dict(map(lambda it: it.split(key_value_separator, 1),
                    filter(lambda it: it != '',
                           list_string.split(list_separator))
                    ))
