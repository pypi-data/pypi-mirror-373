from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

CONSOLIDATED_TRADE_SUMMARY_TABLE_MENUITEM = MenuItem(
    label="Consolidated Trade Summary",
    endpoint="wbportfolio:aumtable-list",
    permission=ItemPermission(
        permissions=["wbportfolio.view_claim"], method=lambda request: is_internal_user(request.user)
    ),
)

PNL_MENUITEM = MenuItem(
    label="Profit & Loss",
    endpoint="wbportfolio:pnltable-list",
    permission=ItemPermission(
        permissions=["wbportfolio.view_claim"], method=lambda request: is_internal_user(request.user)
    ),
)

CLAIM_MENUITEM = MenuItem(
    label="Claims",
    endpoint="wbportfolio:claim-list",
    permission=ItemPermission(permissions=["wbportfolio.view_claim"]),
    add=MenuItem(
        label="Create Claim",
        endpoint="wbportfolio:claim-list",
        permission=ItemPermission(permissions=["wbportfolio.add_claim"]),
    ),
)

NEGATIVEACCOUNTPRODUCT_MENUITEM = MenuItem(
    label="Negative Account per Product",
    endpoint="wbportfolio:negativeaccountproduct-list",
    permission=ItemPermission(method=lambda request: is_internal_user(request.user)),
)

AUM_NNM_PROGRESSION_MENUITEM = MenuItem(
    label="AUM/NNM Progression",
    endpoint="wbportfolio:assetandnetnewmoneyprogression-list",
    permission=ItemPermission(method=lambda request: is_internal_user(request.user)),
)
