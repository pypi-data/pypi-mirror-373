from wbcore.menus import ItemPermission, MenuItem

from wbportfolio.permissions import is_portfolio_manager

EQUITYCASHPOSITION_MENUITEM = MenuItem(
    label="Portfolio Cash Position",
    endpoint="wbportfolio:productcashposition-list",
    permission=ItemPermission(permissions=["wbfdm.view_instrument"], method=is_portfolio_manager),
)
