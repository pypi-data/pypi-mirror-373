from wbcore.menus import ItemPermission, MenuItem

from wbportfolio.permissions import is_manager

GAIN_MENUITEM = MenuItem(
    label="Product Fees",
    endpoint="wbportfolio:feesproductperformance-list",
    permission=ItemPermission(permissions=["wbportfolio.view_product", "wbportfolio.view_fees"], method=is_manager),
)
FEES_MENUITEM = MenuItem(
    label="Fees",
    endpoint="wbportfolio:fees-list",
    permission=ItemPermission(permissions=["wbportfolio.view_fees"], method=is_manager),
)
