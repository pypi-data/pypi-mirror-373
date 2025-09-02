import logging
import importlib

from fyle_integrations_platform_connector import PlatformConnector

from fyle_accounting_mappings.models import ExpenseAttribute
from fyle_accounting_library.common_resources.helpers import get_current_utc_datetime
from fyle_accounting_library.fyle_platform.enums import (
    DefaultFyleConditionsEnum,
    DefaultExpenseAttributeTypeEnum,
    ExpenseFilterCustomFieldTypeEnum,
    DefaultExpenseAttributeDetailEnum
)

workspace_models = importlib.import_module("apps.workspaces.models")
Workspace = workspace_models.Workspace
FyleCredential = workspace_models.FyleCredential

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def check_interval_and_sync_dimension(workspace_id: int, payload: dict) -> None:
    """
    Check Interval and Sync Dimension
    :param workspace_id: Workspace ID
    :param payload: Payload
    :return: None
    """
    workspace = Workspace.objects.get(pk=workspace_id)
    current_utc_datetime = get_current_utc_datetime()
    is_sync_required = (
        payload.get('refresh')
        or workspace.source_synced_at is None
        or (current_utc_datetime - workspace.source_synced_at).days > 0
    )

    if is_sync_required:
        logger.info(f"Syncing Fyle dimensions for workspace {workspace_id}")
        fyle_credentials = FyleCredential.objects.get(workspace_id=workspace_id)
        platform = PlatformConnector(fyle_credentials)
        platform.import_fyle_dimensions()
        workspace.source_synced_at = current_utc_datetime
        workspace.save(update_fields=['source_synced_at', 'updated_at'])
    else:
        logger.info(f"Skipping Fyle dimensions sync for workspace {workspace_id}")


def get_expense_fields(workspace_id: int) -> list[dict]:
    """
    Get Expense Fields
    :param workspace_id: Workspace ID
    :return: List of Expense Fields
    """
    fyle_credentails = FyleCredential.objects.get(workspace_id=workspace_id)
    platform = PlatformConnector(fyle_credentails)
    custom_fields = platform.expense_custom_fields.list_all()

    response = [condition.value for condition in DefaultFyleConditionsEnum]
    custom_field_type_list = [field.value for field in ExpenseFilterCustomFieldTypeEnum]

    for custom_field in custom_fields:
        if custom_field['type'] in custom_field_type_list:
            response.append({
                'field_name': custom_field['field_name'],
                'type': custom_field['type'],
                'is_custom': custom_field['is_custom']
            })

    return response


def get_expense_attribute_types(workspace_id: int) -> list[dict]:
    """
    Get Expense Attribute Fields
    :param workspace_id: Workspace ID
    :return: List of Expense Attribute Fields
    """
    attribute_type_list = [field.value for field in DefaultExpenseAttributeTypeEnum]
    attributes = (
        ExpenseAttribute.objects.filter(workspace_id=workspace_id)
        .exclude(attribute_type__in=attribute_type_list)
        .values('attribute_type', 'display_name')
        .distinct()
    )

    expense_attributes = [DefaultExpenseAttributeDetailEnum.PROJECT.value, DefaultExpenseAttributeDetailEnum.COST_CENTER.value]

    for attribute in attributes:
        expense_attributes.append(attribute)

    return expense_attributes
