from enum import Enum

class ExpenseImportSourceEnum:
    """
    Enum for Expense Import Source
    """
    WEBHOOK = 'WEBHOOK'
    DASHBOARD_SYNC = 'DASHBOARD_SYNC'
    DIRECT_EXPORT = 'DIRECT_EXPORT'
    BACKGROUND_SCHEDULE = 'BACKGROUND_SCHEDULE'
    INTERNAL = 'INTERNAL'
    CONFIGURATION_UPDATE = 'CONFIGURATION_UPDATE'


class ExpenseStateEnum:
    """
    Enum for Expense State
    """
    PAYMENT_PROCESSING = 'PAYMENT_PROCESSING'
    PAID = 'PAID'
    APPROVED = 'APPROVED'


class RoutingKeyEnum:
    """
    Enum for Routing Key
    """
    EXPORT = 'exports.p1'
    UPLOAD_S3 = 'upload.s3'
    UTILITY = 'utility.*'


class SourceAccountTypeEnum:
    """
    Enum for Source Account Type
    """
    PERSONAL_CASH_ACCOUNT = 'PERSONAL_CASH_ACCOUNT'
    PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT = 'PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT'


class FundSourceEnum:
    """
    Enum for Fund Source
    """
    PERSONAL = 'PERSONAL'
    CCC = 'CCC'


class BrandIdEnum:
    """
    Enum for Brand ID
    """
    CO = 'co'
    FYLE = 'fyle'


class ExpenseFundSourceEnum(str, Enum):
    """
    Enum for Expense Fund Source
    """
    PERSONAL = 'PERSONAL'
    CCC = 'CCC'


class ExpenseAccountMapEnum(str, Enum):
    """
    Enum for Expense Account Map
    """
    PERSONAL_CASH_ACCOUNT = 'PERSONAL'
    PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT = 'CCC'



class ExpenseFundSourceKeyMapEnum(str, Enum):
    """
    Enum for Expense Fund Source Map
    """
    CCC_LAST_SYNCED_AT = 'credit_card_last_synced_at'
    CCC_EXPENSE_STATE = 'credit_card_expense_state'
    CCC_EXPENSE_DATE = 'credit_card_expense_date'
    PERSONAL_LAST_SYNCED_AT = 'reimbursable_last_synced_at'
    PERSONAL_EXPENSE_STATE = 'reimbursable_expense_state'
    PERSONAL_EXPENSE_DATE = 'reimbursable_expense_date'


class DefaultExpenseAttributeTypeEnum(str, Enum):
    """
    Enum for Default Expense Attribute Type
    """
    PROJECT = 'PROJECT'
    CATEGORY = 'CATEGORY'
    MERCHANT = 'MERCHANT'
    EMPLOYEE = 'EMPLOYEE'
    TAX_GROUP = 'TAX_GROUP'
    COST_CENTER = 'COST_CENTER'
    CORPORATE_CARD = 'CORPORATE_CARD'


class ExpenseFilterCustomFieldTypeEnum(str, Enum):
    """
    Enum for Expense Filter Custom Field Type
    """
    SELECT = 'SELECT'
    NUMBER = 'NUMBER'
    TEXT = 'TEXT'
    BOOLEAN = 'BOOLEAN'


class ExpenseFieldEnum(str, Enum):
    """
    Enum for Expense Field
    """
    EMPLOYEE_EMAIL = 'employee_email'
    CLAIM_NUMBER = 'claim_number'
    REPORT_TITLE = 'report_title'
    SPENT_AT = 'spent_at'
    CATEGORY = 'category'


class ExpenseFilterRankEnum(int, Enum):
    """
    Enum for Expense Filter Rank
    """
    ONE = 1
    TWO = 2


class ExpenseFilterJoinByEnum(str, Enum):
    """
    Enum for Expense Filter Join By
    """
    AND = 'AND'
    OR = 'OR'


class ExpenseFilterConditionEnum(str, Enum):
    """
    Enum for Expense Filter Condition
    """
    IS_NULL = 'isnull'
    IN = 'in'
    NOT_IN = 'not_in'
    TRUE = 'true'
    FALSE = 'false'
    ONE = 1
    SELECT = 'SELECT'
    NUMBER = 'NUMBER'
    BOOLEAN = 'BOOLEAN'
    CATEGORY = 'category'


class ExpenseFilterOperatorEnum(str, Enum):
    """
    Enum for Expense Filter Operator
    """
    IS_NULL = 'isnull'
    IN = 'in'
    IEXACT = 'iexact'
    ICASECONTAINS = 'icontains'
    LT = 'lt'
    LTE = 'lte'
    NOT_IN = 'not_in'


class AdvancedSearchFilterFieldEnum(str, Enum):
    """
    Enum for Advanced Search Filter Field
    """
    GTE = 'gte'
    LTE = 'lte'
    IN = 'in'
    BOOL_TRUE = 'true'
    BOOL_FALSE = 'false'
    UPDATED_AT = 'updated_at'
    ICONTAINS = 'icontains'
    EXACT = 'exact'
    ID__IN = 'id__in'
    TYPE__IN = 'type__in'
    STATUS__IN = 'status__in'
    IS_SKIPPED = 'is_skipped'
    UPDATED_AT__GTE = 'updated_at__gte'
    UPDATED_AT__LTE = 'updated_at__lte'
    EXPENSE_NUMBER = 'expense_number'
    EMPLOYEE_NAME = 'employee_name'
    EMPLOYEE_EMAIL = 'employee_email'
    CLAIM_NUMBER = 'claim_number'


class ExpenseStateChangeEventEnum(str, Enum):
    """
    Enum for Expense State Change Event
    """
    ADMIN_APPROVED = 'ADMIN_APPROVED'
    APPROVED = 'APPROVED'
    STATE_CHANGE_PAYMENT_PROCESSING = 'STATE_CHANGE_PAYMENT_PROCESSING'
    PAID = 'PAID'


class WebhookCallbackActionEnum(str, Enum):
    """
    Enum for Webhook Callback Action
    """
    ACCOUNTING_EXPORT_INITIATED = 'ACCOUNTING_EXPORT_INITIATED'
    UPDATED_AFTER_APPROVAL = 'UPDATED_AFTER_APPROVAL'


class WebhookCallbackResourceEnum(str, Enum):
    """
    Enum for Webhook Callback Resource
    """
    EXPENSE = 'EXPENSE'


class ExpenseAccountTypeEnum(str, Enum):
    """
    Enum for Expense Account Type
    """
    PERSONAL = 'PERSONAL_CASH_ACCOUNT'
    CCC = 'PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT'


class DefaultExpenseAttributeDetailEnum(Enum):
    """
    Enum for Default Expense Attribute Detail
    """
    PROJECT = {
        'attribute_type': DefaultExpenseAttributeTypeEnum.PROJECT.value,
        'display_name': DefaultExpenseAttributeTypeEnum.PROJECT.name.replace('_', ' ').title()
    }
    COST_CENTER = {
        'attribute_type': DefaultExpenseAttributeTypeEnum.COST_CENTER.value,
        'display_name': DefaultExpenseAttributeTypeEnum.COST_CENTER.name.replace('_', ' ').title()
    }
    CATEGORY = {
        'attribute_type': DefaultExpenseAttributeTypeEnum.CATEGORY.value,
        'display_name': DefaultExpenseAttributeTypeEnum.CATEGORY.name.replace('_', ' ').title()
    }
    MERCHANT = {
        'attribute_type': DefaultExpenseAttributeTypeEnum.MERCHANT.value,
        'display_name': DefaultExpenseAttributeTypeEnum.MERCHANT.name.replace('_', ' ').title()
    }
    EMPLOYEE = {
        'attribute_type': DefaultExpenseAttributeTypeEnum.EMPLOYEE.value,
        'display_name': DefaultExpenseAttributeTypeEnum.EMPLOYEE.name.replace('_', ' ').title()
    }
    TAX_GROUP = {
        'attribute_type': DefaultExpenseAttributeTypeEnum.TAX_GROUP.value,
        'display_name': DefaultExpenseAttributeTypeEnum.TAX_GROUP.name.replace('_', ' ').title()
    }
    CORPORATE_CARD = {
        'attribute_type': DefaultExpenseAttributeTypeEnum.CORPORATE_CARD.value,
        'display_name': DefaultExpenseAttributeTypeEnum.CORPORATE_CARD.name.replace('_', ' ').title()
    }


class DefaultFyleConditionsEnum(Enum):
    """
    Enum for Default Fyle Conditions
    """
    EMPLOYEE_EMAIL = {
        'field_name': ExpenseFieldEnum.EMPLOYEE_EMAIL.value,
        'type': ExpenseFilterCustomFieldTypeEnum.SELECT.value,
        'is_custom': False
    }
    CLAIM_NUMBER = {
        'field_name': ExpenseFieldEnum.CLAIM_NUMBER.value,
        'type': ExpenseFilterCustomFieldTypeEnum.TEXT.value,
        'is_custom': False
    }
    REPORT_TITLE = {
        'field_name': ExpenseFieldEnum.REPORT_TITLE.value,
        'type': ExpenseFilterCustomFieldTypeEnum.TEXT.value,
        'is_custom': False
    }
    SPENT_AT = {
        'field_name': ExpenseFieldEnum.SPENT_AT.value,
        'type': 'DATE',
        'is_custom': False
    }
    CATEGORY = {
        'field_name': ExpenseFieldEnum.CATEGORY.value,
        'type': ExpenseFilterCustomFieldTypeEnum.SELECT.value,
        'is_custom': False
    }
