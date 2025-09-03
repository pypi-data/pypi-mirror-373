import signal
import traceback
from datetime import timedelta
from functools import wraps
from multiprocessing import Pool
from os import getpid, kill
from sys import exit
from threading import Condition, Event
from typing import Callable

from django.core.management.base import BaseCommand

from papyru.utils import limited_runtime, log
from papyru.varspool import add_status, fetch_jobs
from papyru.varspool.types import Job, StatusConflict

from .config import VarspoolJobProcessorConfig
from .types import JobProcessorStatus, JobResult

g_exit = Event()


def loop_until(time_range: timedelta):
    '''
    Decorates a function which performs a single loop step.

    Calls the function as long as the according process has neither
    received SIGTERM nor the given time range has been exceeded.
    '''

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            state = {'received_sigterm': False}

            def handle_sigterm(*args, **kwargs):
                log('caught SIGTERM. will shutdown gracefully.')
                state['received_sigterm'] = True
                g_exit.set()

            signal.signal(signal.SIGTERM, handle_sigterm)

            with limited_runtime(time_range) as has_runtime_left:
                while has_runtime_left() and not state['received_sigterm']:
                    func(*args, **kwargs)
        return wrapper
    return decorator


def handle_job(job: Job,
               job_processor_status: JobProcessorStatus,
               processing_fn: Callable):
    job_in_progress = True

    try:
        def handle_sigterm(*args, **kwargs):
            try:
                if job_in_progress:
                    log('abort job %d because of sigterm' % job.id)
                    add_status(job, job_processor_status.ABORT,
                               {'reason': 'graceful command shutdown'})
            except StatusConflict as ex:
                log('StatusConflict for job %d: %s' % (job.id, str(ex)),
                    level='warning')
            except Exception as ex:
                log(traceback.format_exc(), level='error')
                log('[ALERT] could not abort job %d: %s: %s' % (
                    job.id, type(ex).__name__, str(ex)),
                    level='error')
            exit(0)

        signal.signal(signal.SIGTERM, handle_sigterm)

        log('processing job %d.' % job.id)

        try:
            job = add_status(job, job_processor_status.IN_PROGRESS)
        except StatusConflict:
            log('job %d is already in progress. skipping.' % job.id)
            job_in_progress = False
            return

        try:
            result = processing_fn(job)
        except Exception as ex:
            formatted_traceback = traceback.format_exc()
            formatted_exc = ('uncaught error (%s): %s'
                             % (type(ex).__name__, str(ex)))
            result = JobResult(
                job_processor_status.FAILED,
                {'reason': formatted_exc, 'traceback': formatted_traceback})

        job = add_status(job, result.status, result.data)
        log('processed job %d.' % job.id)
    except Exception as ex:
        log(traceback.format_exc(), level='error')
        log('[ALERT] could not process job %d: %s: %s' % (
            job.id, type(ex).__name__, str(ex)),
            level='error')

    job_in_progress = False


def enter_job_loop(config: VarspoolJobProcessorConfig):
    '''
    Main job loop launching a process pool and asynchronously calling
    job processing functions.
    '''

    try:
        log('checking config...')

        if not isinstance(config, VarspoolJobProcessorConfig):
            raise RuntimeError(
                'could not start job loop due to invalid config.')

        log('- queue url: %s' % config.queue_url)

        active_jobs = 0
        active_jobs_reduced = Condition()

        def reduce_active_jobs(exc=None):
            nonlocal active_jobs

            if exc is not None:
                log('[ALERT] unhandled critical exception while processing '
                    'job: %s: %s' % (type(exc).__name__, str(exc)),
                    level='error')

            with active_jobs_reduced:
                active_jobs -= 1
                active_jobs_reduced.notify()

        def wait_for_free_slot(timeout: float):
            with active_jobs_reduced:
                active_jobs_reduced.wait(timeout)

        with Pool(processes=config.max_parallel_job_count) as pool:
            @loop_until(
                time_range=timedelta(minutes=config.max_runtime_in_minutes))
            def wrapper():
                nonlocal active_jobs

                log('fetching jobs...')

                if (active_jobs >= config.max_parallel_job_count):
                    log('too many active jobs. waiting for a free slot.')
                    wait_for_free_slot(config.loop_cooldown_in_seconds)
                    return

                jobs = fetch_jobs(config.queue_url,
                                  config.job_processor_status.OPEN,
                                  config.max_parallel_job_count - active_jobs)

                if len(jobs) == 0:
                    if config.wait_for_further_jobs:
                        log('no jobs to process. waiting...')
                        g_exit.wait(config.loop_cooldown_in_seconds)
                    else:
                        log('no jobs and no further runtime. Going to stop '
                            'command')
                        kill(getpid(), signal.SIGTERM)
                    return

                for job in jobs:
                    log('dispatching job %d.' % job.id)
                    active_jobs += 1
                    pool.apply_async(
                        func=handle_job,
                        args=(job,
                              config.job_processor_status,
                              config.job_handler),
                        callback=reduce_active_jobs,
                        error_callback=reduce_active_jobs)
                    log('dispatched job %d.' % job.id)
            wrapper()

    except Exception as ex:
        log(traceback.format_exc(), level='error')
        log('[ALERT] critical error occurred: %s (%s). '
            'awaiting end of failure backoff...'
            % (type(ex).__name__, str(ex)),
            level='error')

        g_exit.wait(config.failure_backoff_in_seconds
                    if hasattr(config, 'failure_backoff_in_seconds')
                    else (VarspoolJobProcessorConfig
                          .DEFAULT_FAILURE_BACKOFF_IN_SECONDS))
        exit(1)


class VarspoolJobProcessorBaseCommand(BaseCommand):
    config: VarspoolJobProcessorConfig = None

    def handle(self, *args, **kwargs):
        log('varspool job processor started.')

        log('entering job loop.')
        enter_job_loop(self.config)
        log('goodbye.')
