import logging
import importlib

from rest_framework.views import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from fyle.platform.exceptions import (
    NoPrivilegeError,
    RetryException,
    InvalidTokenError as FyleInvalidTokenError
)

fyle_models = importlib.import_module("apps.fyle.models")
Expense = fyle_models.Expense

workspace_models = importlib.import_module("apps.workspaces.models")
FyleCredential = workspace_models.FyleCredential
Workspace = workspace_models.Workspace

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def handle_webhook_callback_exceptions() -> callable:
    """
    Decorator to handle exceptions in webhook callbacks
    :return: callable
    """
    def decorator(func: callable) -> callable:
        def new_fn(*args, **kwargs) -> callable:
            try:
                return func(*args, **kwargs)
            except Expense.DoesNotExist:
                return Response(data={'message': 'Expense not found'}, status=status.HTTP_400_BAD_REQUEST)

            except FyleCredential.DoesNotExist:
                return Response(data={'message': 'Fyle credentials not found in workspace'}, status=status.HTTP_400_BAD_REQUEST)

            except Workspace.DoesNotExist:
                return Response(data={'message': 'Workspace does not exist'}, status=status.HTTP_400_BAD_REQUEST)

            except ValidationError as exception:
                logger.exception(exception)
                return Response({"message": exception.detail}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as exception:
                logger.exception(exception)
                return Response(
                    data={'message': 'An unhandled error has occurred, please re-try later'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return new_fn

    return decorator


def handle_exceptions() -> callable:
    """
    Decorator to handle general exceptions
    :return: callable
    """
    def decorator(func: callable) -> callable:
        def new_fn(*args, **kwargs) -> callable:
            try:
                return func(*args, **kwargs)

            except FyleCredential.DoesNotExist:
                return Response(data={'message': 'Fyle credentials not found in workspace'}, status=status.HTTP_400_BAD_REQUEST)

            except NoPrivilegeError:
                return Response(data={'message': 'User does not have enough privileges. Fyle Credentials Invalid / Admin Disabled'}, status=status.HTTP_400_BAD_REQUEST)

            except RetryException:
                return Response(data={'message': 'Fyle API limit exceeded. Please try again later'}, status=status.HTTP_400_BAD_REQUEST)

            except FyleInvalidTokenError:
                return Response(data={'message': 'Fyle token is invalid'}, status=status.HTTP_400_BAD_REQUEST)

            except ValidationError as exception:
                logger.exception(exception)
                return Response({"message": exception.detail}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as exception:
                logger.exception(exception.__dict__)
                return Response(
                    data={'message': 'An unhandled error has occurred, please re-try later'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return new_fn

    return decorator
