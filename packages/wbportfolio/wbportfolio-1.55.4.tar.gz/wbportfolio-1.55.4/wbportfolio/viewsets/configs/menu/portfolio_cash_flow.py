from wbcore.menus import ItemPermission, MenuItem

from wbportfolio.permissions import is_portfolio_manager

PORTFOLIO_DAILY_CASH_FLOW = MenuItem(
    label="Daily Portfolio Cash Flow",
    endpoint="wbportfolio:portfoliocashflow-list",
    permission=ItemPermission(permissions=["wbportfolio.view_portfolio"], method=is_portfolio_manager),
)
