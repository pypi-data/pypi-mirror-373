from typing import Any

import django_filters
from django.db import models

from .enums import AdvancedSearchFilterFieldEnum as AdvSeachFieldEnum


class ExpenseGroupSettingsAdapter:
    """
    Adapter class to handle different column names across integrations
    """
    # Mapping of column names for different integrations
    COLUMN_MAPPINGS = {
        'default': {
            'expense_state': 'expense_state',
            'ccc_expense_state': 'ccc_expense_state'
        },
        'sage_desktop': {
            'expense_state': 'reimbursable_expense_state',
            'ccc_expense_state': 'credit_card_expense_state'
        }
    }
    COLUMN_MAPPINGS['quickbooks_connector'] = dict(COLUMN_MAPPINGS['sage_desktop'])
    COLUMN_MAPPINGS['sage_file_export'] = dict(COLUMN_MAPPINGS['sage_desktop'])
    COLUMN_MAPPINGS['xero'] = dict(COLUMN_MAPPINGS['default'])
    COLUMN_MAPPINGS['xero']['expense_state'] = 'reimbursable_expense_state'

    def __init__(self, settings_model: Any, integration_type: str = 'default'):
        """
        Initialize adapter with settings model and integration type
        :param settings_model: Django model instance containing settings
        :param integration_type: Type of integration (e.g. 'default', 'xero')
        """
        self.settings = settings_model
        self.mapping = self.COLUMN_MAPPINGS.get(integration_type, self.COLUMN_MAPPINGS['default'])

    def __getattr__(self, name: str) -> Any:
        """
        Get attribute using the mapping
        :param name: Attribute name
        :return: Mapped value from settings
        """
        if name in self.mapping:
            mapped_name = self.mapping[name]
            # Safely get the mapped attribute, return None if it doesn't exist
            return getattr(self.settings, mapped_name, None)

        return getattr(self.settings, name)


class AdvanceSearchFilter(django_filters.FilterSet):
    """
    Advance Search Filter Base Class
    """
    def filter_queryset(self, queryset: models.QuerySet) -> models.QuerySet:
        """
        Filter queryset
        :param queryset: Queryset
        :return: Filtered queryset
        """
        or_filtered_queryset = queryset.none()
        or_filter_fields = getattr(self.Meta, 'or_fields', [])
        or_field_present = False

        for field_name in self.Meta.fields:
            value = self.data.get(field_name)
            if value:
                if field_name == AdvSeachFieldEnum.IS_SKIPPED.value:
                    value = True if str(value) == AdvSeachFieldEnum.BOOL_TRUE.value else False

                field_list = [
                    AdvSeachFieldEnum.STATUS__IN.value,
                    AdvSeachFieldEnum.TYPE__IN.value,
                    AdvSeachFieldEnum.ID__IN.value
                ]

                if field_name in field_list:
                    value_lt = value.split(',')
                    filter_instance = self.filters[field_name]
                    queryset = filter_instance.filter(queryset, value_lt)
                else:
                    filter_instance = self.filters[field_name]
                    queryset = filter_instance.filter(queryset, value)

        for field_name in or_filter_fields:
            value = self.data.get(field_name)
            if value:
                or_field_present = True
                filter_instance = self.filters[field_name]
                field_filtered_queryset = filter_instance.filter(queryset, value)
                or_filtered_queryset |= field_filtered_queryset

        if or_field_present:
            queryset = queryset & or_filtered_queryset
            return queryset

        return queryset
