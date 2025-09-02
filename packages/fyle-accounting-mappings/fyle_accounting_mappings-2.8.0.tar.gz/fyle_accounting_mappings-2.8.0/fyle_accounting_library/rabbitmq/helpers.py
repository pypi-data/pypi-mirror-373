import logging
from typing import List
from django.core.management import call_command
from django.utils.module_loading import import_string

from .data_class import Task
from .models import FailedEvent


logger = logging.getLogger(__name__)


class TaskChainRunner:
    """
    Helper class for executing a chain of tasks
    """

    def run(self, chain_tasks: List[Task], workspace_id: int):
        """
        Execute a chain of tasks
        
        Args:
            chain_tasks: List of Task objects containing target and arguments
        """
        for task in chain_tasks:
            try:
                import_string(task.target)(*task.args, **task.kwargs)
            except Exception as e:
                logger.error(f"Error while executing {task.target} with args {task.args} and kwargs {task.kwargs}: {e}")
                FailedEvent.objects.create(
                    routing_key=task.target,
                    payload=task.to_json(),
                    workspace_id=workspace_id,
                    error_traceback=str(e)
                )


def create_cache_table():
    """
    Create cache table
    """
    try:
        logger.info('Creating cache table if it does not exist...')
        call_command('createcachetable', database='cache_db', verbosity=0)
        logger.info('Cache table creation completed successfully')
    except Exception as e:
        logger.error('Error creating cache table: %s', str(e))
