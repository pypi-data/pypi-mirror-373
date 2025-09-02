from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

OrderProposalMenuItem = MenuItem(
    label="Order Proposals",
    endpoint="wbportfolio:orderproposal-list",
    endpoint_get_parameters={"waiting_for_input": True},
    permission=ItemPermission(
        permissions=["wbportfolio.view_orderproposal"], method=lambda request: is_internal_user(request.user)
    ),
)
