from wbcore.menus import ItemPermission, MenuItem

ACCOUNT_RECONCILIATION_MENU_ITEM = MenuItem(
    label="Account Reconciliations",
    endpoint="wbportfolio:accountreconciliation-list",
    permission=ItemPermission(permissions=["wbportfolio.view_accountreconciliation"]),
)
