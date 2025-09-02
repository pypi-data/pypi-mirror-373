import logging
import importlib

from typing import List, Any

from django.db import models
from django.db.models import Q
from rest_framework.exceptions import ValidationError

workspace_models = importlib.import_module("apps.workspaces.models")
Workspace = workspace_models.Workspace

from .enums import (
    FundSourceEnum,
    ExpenseStateEnum,
    ExpenseFilterRankEnum,
    SourceAccountTypeEnum,
    ExpenseFilterJoinByEnum,
    ExpenseFilterConditionEnum as OperatorEnum
)
from .constants import REIMBURSABLE_IMPORT_STATE, CCC_IMPORT_STATE
from .models import ExpenseGroupSettingsAdapter

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def get_expense_import_states(expense_group_settings: Any, integration_type: str = 'default') -> List[str]:
    """
    Get expense import state
    :param expense_group_settings: expense group settings model instance
    :param integration_type: Type of integration (e.g. 'default', 'xero')
    :return: expense import state
    """
    expense_group_settings = ExpenseGroupSettingsAdapter(expense_group_settings, integration_type)
    expense_import_state = set()

    if expense_group_settings.ccc_expense_state == ExpenseStateEnum.APPROVED:
        expense_import_state = {ExpenseStateEnum.APPROVED, ExpenseStateEnum.PAYMENT_PROCESSING, ExpenseStateEnum.PAID}

    if expense_group_settings.expense_state == ExpenseStateEnum.PAYMENT_PROCESSING:
        expense_import_state.add(ExpenseStateEnum.PAYMENT_PROCESSING)
        expense_import_state.add(ExpenseStateEnum.PAID)

    if expense_group_settings.expense_state == ExpenseStateEnum.PAID or expense_group_settings.ccc_expense_state == ExpenseStateEnum.PAID:
        expense_import_state.add(ExpenseStateEnum.PAID)

    return list(expense_import_state)


def filter_expenses_based_on_state(expenses: List[Any], expense_group_settings: Any, integration_type: str = 'default'):
    """
    Filter expenses based on the expense state
    :param expenses: list of expenses
    :param expense_group_settings: expense group settings model instance
    :param integration_type: Type of integration (e.g. 'default', 'xero')
    :return: list of filtered expenses
    """
    expense_group_settings = ExpenseGroupSettingsAdapter(expense_group_settings, integration_type)

    allowed_reimbursable_import_state = REIMBURSABLE_IMPORT_STATE.get(expense_group_settings.expense_state)
    reimbursable_expenses = list(filter(lambda expense: expense['source_account_type'] == SourceAccountTypeEnum.PERSONAL_CASH_ACCOUNT and expense['state'] in allowed_reimbursable_import_state, expenses))

    allowed_ccc_import_state = CCC_IMPORT_STATE.get(expense_group_settings.ccc_expense_state)
    ccc_expenses = list(filter(lambda expense: expense['source_account_type'] == SourceAccountTypeEnum.PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT and expense['state'] in allowed_ccc_import_state, expenses))

    return reimbursable_expenses + ccc_expenses


def get_source_account_types_based_on_export_modules(reimbursable_export_module: str, ccc_export_module: str) -> List[str]:
    """
    Get source account types based on the export modules
    :param reimbursable_export_module: reimbursable export module
    :param ccc_export_module: ccc export module
    :return: list of source account types
    """
    source_account_types = []
    if reimbursable_export_module:
        source_account_types.append(SourceAccountTypeEnum.PERSONAL_CASH_ACCOUNT)
    if ccc_export_module:
        source_account_types.append(SourceAccountTypeEnum.PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT)

    return source_account_types


def get_fund_source_based_on_export_modules(reimbursable_export_module: str, ccc_export_module: str) -> List[str]:
    """
    Get fund source based on the export modules
    :param reimbursable_export_module: reimbursable export module
    :param ccc_export_module: ccc export module
    :return: list of fund source
    """
    fund_source = []
    if reimbursable_export_module:
        fund_source.append(FundSourceEnum.PERSONAL)
    if ccc_export_module:
        fund_source.append(FundSourceEnum.CCC)

    return fund_source


def assert_valid_callback_request(workspace_id: int, org_id: str) -> None:
    """
    Assert if the callback request is valid
    :param workspace_id: workspace id
    :param org_id: org id
    :return: None
    """
    workspace = Workspace.objects.get(org_id=org_id)
    if workspace.id != workspace_id:
        raise ValidationError('Workspace id does not match with the org id in the request')



def construct_expense_filter_query(expense_filters: list[models.Model]) -> Q:
    """
    Construct expense filter query
    :param expense_filters: expense filters
    :return: Expense filter query
    """
    expense_filter_query = None
    join_by = None

    for expense_filter in expense_filters:
        constructed_expense_filter = construct_expense_filter(expense_filter)

        if expense_filter.rank == ExpenseFilterRankEnum.ONE.value:
            expense_filter_query = constructed_expense_filter

        elif expense_filter.rank != ExpenseFilterRankEnum.ONE.value:
            if join_by == ExpenseFilterJoinByEnum.AND.value:
                expense_filter_query = expense_filter_query & (constructed_expense_filter)
            else:
                expense_filter_query = expense_filter_query | (constructed_expense_filter)

        join_by = expense_filter.join_by

    return expense_filter_query


def construct_expense_filter(expense_filter: models.Model) -> Q:
    """
    Construct expense filter
    :param expense_filter: expense filter
    :return: constructed expense filter
    """
    constructed_expense_filter = {}

    if expense_filter.is_custom:
        if expense_filter.operator != OperatorEnum.IS_NULL.value:
            if expense_filter.custom_field_type == OperatorEnum.SELECT.value and expense_filter.operator == OperatorEnum.NOT_IN.value:
                filter1 = {
                    f'custom_properties__{expense_filter.condition}__in': expense_filter.values
                }
                constructed_expense_filter = ~Q(**filter1)
            else:
                if expense_filter.custom_field_type == OperatorEnum.NUMBER.value:
                    expense_filter.values = [int(value) for value in expense_filter.values]
                if expense_filter.custom_field_type == OperatorEnum.BOOLEAN.value:
                    expense_filter.values[0] = True if expense_filter.values[0] == OperatorEnum.TRUE.value else False

                filter1 = {
                    f'custom_properties__{expense_filter.condition}__{expense_filter.operator}':
                        expense_filter.values[0] if len(expense_filter.values) == OperatorEnum.ONE.value and expense_filter.operator != OperatorEnum.IN.value
                        else expense_filter.values
                }
                constructed_expense_filter = Q(**filter1)

        elif expense_filter.operator == OperatorEnum.IS_NULL.value:
            expense_filter_value: bool = True if expense_filter.values[0].lower() == OperatorEnum.TRUE.value else False
            filter1 = {
                f'custom_properties__{expense_filter.condition}__isnull': expense_filter_value
            }
            filter2 = {
                f'custom_properties__{expense_filter.condition}__exact': None
            }
            if expense_filter_value:
                constructed_expense_filter = Q(**filter1) | Q(**filter2)
            else:
                constructed_expense_filter = ~Q(**filter2)

    elif expense_filter.condition == OperatorEnum.CATEGORY.value and expense_filter.operator == OperatorEnum.NOT_IN.value and not expense_filter.is_custom:
        filter1 = {
            f'{expense_filter.condition}__in': expense_filter.values
        }
        constructed_expense_filter = ~Q(**filter1)

    else:
        filter1 = {
            f'{expense_filter.condition}__{expense_filter.operator}':
                expense_filter.values[0] if len(expense_filter.values) == OperatorEnum.ONE.value and expense_filter.operator != OperatorEnum.IN.value
                else expense_filter.values
        }
        constructed_expense_filter = Q(**filter1)

    return constructed_expense_filter
