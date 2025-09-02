from wbcore.menus import ItemPermission, MenuItem

from wbportfolio.permissions import is_analyst, is_portfolio_manager

ASSETPOSITION_MENUITEM = MenuItem(
    label="Invested Asset Positions",
    endpoint="wbportfolio:assetpositiongroupby-list",
    permission=ItemPermission(permissions=["wbfdm.view_instrument"], method=is_analyst),
)

AGGREGATED_ASSETPOSITION_LIQUIDITY_MENUITEM = MenuItem(
    label="Asset Positions Liquidity Table",
    endpoint="wbportfolio:aggregatedassetpositionliquidity-list",
    permission=ItemPermission(permissions=["wbfdm.view_instrument"], method=is_portfolio_manager),
)
