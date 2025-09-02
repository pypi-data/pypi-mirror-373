from wbcore.menus import ItemPermission, MenuItem
from wbportfolio.permissions import is_manager

REBATE_MENUITEM = MenuItem(
    label="Rebates",
    endpoint="wbcommission:rebatetable-list",
    permission=ItemPermission(permissions=["wbcommission.view_rebate"]),
)
REBATE_MARGINALITY_MENUITEM = MenuItem(
    label="Marginality",
    endpoint="wbcommission:rebatemarginalitytable-list",
    permission=ItemPermission(permissions=["wbcommission.view_rebate"], method=is_manager),
)
