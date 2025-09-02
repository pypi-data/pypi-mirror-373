from wbcore.menus import ItemPermission, MenuItem

from wbportfolio.permissions import is_portfolio_manager

ADJUSTMENT_MENUITEM = MenuItem(
    label="Adjustment",
    endpoint="wbportfolio:adjustment-list",
    permission=ItemPermission(permissions=["wbportfolio.view_adjustment"], method=is_portfolio_manager),
)
