from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

TASK_MENUITEM = MenuItem(
    label="Tasks",
    endpoint="wbtasks:task-list",
    add=MenuItem(label="Create Task", endpoint="wbtasks:task-list"),
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbtasks.view_task"]
    ),
)
