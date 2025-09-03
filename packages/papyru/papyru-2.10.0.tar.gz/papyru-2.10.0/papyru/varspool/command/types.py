from dataclasses import dataclass, field


@dataclass(frozen=True)
class JobProcessorStatus:
    '''
    - `OPEN`: Jobs with this status are processed.
    - `IN_PROGRESS`: Jobs get this status when the process has been started.
    - `FAILED`: Jobs get this status if the process failed.
    - `ABORT`: Jobs get this status when the process is canceled. This is the
      case when the runtime is exhausted or was interrupted by SIGTERM.
    '''
    OPEN: str = 'open'
    IN_PROGRESS: str = 'in_progress'
    FAILED: str = 'failed'
    ABORT: str = 'open'


@dataclass
class JobResult:
    status: str
    data: dict = field(default_factory=lambda: {})
