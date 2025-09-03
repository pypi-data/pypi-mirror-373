'''
A base class for RESTful resource implementations to be used as Django views.
Dispatching is handled based on the HTTP method of the request. When handling
a request, the instance-method named exactly like the lowercase version of
the HTTP method is called. The response depends on the control flow of the
specific handler.
If it returns normally, whatever value is returned from the handler is the
response. Otherwise the `Resource` tries to emit a meaningful error message.

- If a `Problem` was raised, it is returned as a response.
- If an ObjectDoesNotExist exception was raised, a `Problem.not_found` instance
  is returned.
- Otherwise the exception is wrapped in a `Problem.internal_server_error`.

All Problems belonging to the 5XX-class of HTTP errors are logged to stdout.
'''

from django.core.exceptions import ObjectDoesNotExist

from papyru.logger import LogSequence, log_root
from papyru.logger_stdout import StdoutSink
from papyru.logger_types import Message, Sequence
from papyru.problem import Problem

# defined in RFC 7231
HTTP_METHODS = set(['get', 'head', 'post', 'put', 'delete', 'connect',
                    'options', 'trace'])


class ResourceSink(StdoutSink):
    LOG_ALL_MESSAGES = False

    def commit(self, item):
        if (isinstance(item, Sequence) and item.resolution < Message.WARNING
                and self.LOG_ALL_MESSAGES is False):
            return

        super().commit(item)


class Resource:
    @log_root(ResourceSink())
    def __call__(self, request, *args):
        try:
            try:
                method = getattr(self.__class__, request.method.lower())
            except AttributeError:
                if (request.method.lower() == 'head' and
                        getattr(self.__class__, 'get', False)):
                    method = _simple_head
                else:
                    method = _method_not_allowed(
                        allowed=set(dir(self.__class__)) & HTTP_METHODS)

            def respond():
                return method(self, request, *args)

            should_log_access = getattr(method, '_should_log_access', True)

            if should_log_access:
                request_id = request.headers.get('pap-request-id', None)

                with LogSequence('%s%s %s' % (('[%s] ' % request_id
                                               if request_id is not None
                                               else ''),
                                              request.method,
                                              request.get_full_path())):
                    return respond()
            else:
                return respond()

        except Problem as problem:
            return problem.to_response()

        except ObjectDoesNotExist:
            return Problem.not_found().to_response()

        except NotImplementedError:
            return Problem.not_implemented().to_response()

        except Exception as exc:
            return Problem.internal_server_error(
                'unexpected error: %s' % exc).to_response()


def no_access_log(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    wrapper._should_log_access = False
    return wrapper


def _simple_head(self, request, *args):
    method = getattr(self.__class__, 'get')
    resp = method(self, request, *args)
    resp.content = ''
    return resp


def _method_not_allowed(allowed):
    def wrapped(*args, **kwargs):
        raise Problem.method_not_allowed(allowed)

    return wrapped
