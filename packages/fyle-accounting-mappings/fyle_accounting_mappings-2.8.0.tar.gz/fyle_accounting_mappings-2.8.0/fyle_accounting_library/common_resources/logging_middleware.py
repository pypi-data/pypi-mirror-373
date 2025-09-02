import logging
import random
import string
import os
import inspect


logger = logging.getLogger(__name__)
logger.level = logging.WARNING


def generate_worker_id():
    return 'worker_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


def set_worker_id_in_env():
    worker_id = generate_worker_id()
    os.environ['WORKER_ID'] = worker_id


def get_logger():
    if 'WORKER_ID' not in os.environ:
        set_worker_id_in_env()
    worker_id = os.environ['WORKER_ID']
    extra = {'worker_id': worker_id}
    updated_logger = logging.LoggerAdapter(logger, extra)
    updated_logger.setLevel(logging.INFO)

    return updated_logger


def get_caller_info() -> str:
    """
    Get information about the caller of the current function
    Returns a string containing the caller's module name and function name
    """
    frame = inspect.currentframe()
    if frame:
        # Get the caller's frame (2 levels up from current frame)
        caller_frame = frame.f_back.f_back
        if caller_frame:
            # Get the caller's module and function name
            module_name = caller_frame.f_globals.get('__name__', 'unknown')
            function_name = caller_frame.f_code.co_name
            return f"{module_name}.{function_name}"
    return "unknown"


class WorkerIDFilter(logging.Filter):
    def filter(self, record):
        worker_id = getattr(record, 'worker_id', '')
        record.worker_id = worker_id
        return True
