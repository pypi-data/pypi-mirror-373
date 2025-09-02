from wbcore.menus import ItemPermission, MenuItem

PortfolioMenuItem = MenuItem(
    label="Portfolios",
    endpoint="wbportfolio:portfolio-list",
    permission=ItemPermission(permissions=["wbportfolio.view_portfolio"]),
)


ModelPortfolioMenuItem = MenuItem(
    label="Managed Portfolios",
    endpoint="wbportfolio:portfolio-list",
    endpoint_get_parameters={"is_manageable": True},
    permission=ItemPermission(permissions=["wbportfolio.view_portfolio"]),
)
