from wbcore.menus import ItemPermission, MenuItem

REPORT_MENUITEM = MenuItem(
    label="Reports",
    endpoint="wbreport:report-list",
    permission=ItemPermission(permissions=["wbreport.view_report"]),
    endpoint_get_parameters={"parent_report__isnull": True},
)
