from .enums import ExpenseImportSourceEnum, ExpenseStateEnum

REIMBURSABLE_IMPORT_STATE = {
    ExpenseStateEnum.PAYMENT_PROCESSING: [ExpenseStateEnum.PAYMENT_PROCESSING, ExpenseStateEnum.PAID],
    ExpenseStateEnum.PAID: [ExpenseStateEnum.PAID]
}

CCC_IMPORT_STATE = {
    ExpenseStateEnum.APPROVED: [ExpenseStateEnum.APPROVED, ExpenseStateEnum.PAYMENT_PROCESSING, ExpenseStateEnum.PAID],
    ExpenseStateEnum.PAID: [ExpenseStateEnum.PAID]
}

IMPORTED_FROM_CHOICES =  (
    (ExpenseImportSourceEnum.WEBHOOK, 'WEBHOOK'),
    (ExpenseImportSourceEnum.DASHBOARD_SYNC, 'DASHBOARD_SYNC'),
    (ExpenseImportSourceEnum.DIRECT_EXPORT, 'DIRECT_EXPORT'),
    (ExpenseImportSourceEnum.BACKGROUND_SCHEDULE, 'BACKGROUND_SCHEDULE'),
    (ExpenseImportSourceEnum.INTERNAL, 'INTERNAL')
)
