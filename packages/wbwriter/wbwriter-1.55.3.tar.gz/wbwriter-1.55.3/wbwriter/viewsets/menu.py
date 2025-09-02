from wbcore.menus import ItemPermission, Menu, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

WRITER_MENU = Menu(
    label="Writer",
    items=[
        MenuItem(
            label="Article",
            endpoint="wbwriter:article-list",
            add=MenuItem(
                label="Create an article",
                endpoint="wbwriter:article-list",
            ),
            permission=ItemPermission(
                method=lambda request: is_internal_user(request.user), permissions=["wbwriter.view_article"]
            ),
        ),
        # MenuItem(
        #     label="DDQ",
        #     endpoint="wbwriter:ddq-list",
        #     add=MenuItem(
        #         label="Create a DDQ related entry",
        #         endpoint="wbwriter:ddq-list",
        #     ),
        #     permission=ItemPermission(permissions=["wbwriter.view_article"]),
        # ),
        MenuItem(
            label="Articles to review",
            endpoint="wbwriter:review-article-list",
            permission=ItemPermission(
                method=lambda request: is_internal_user(request.user), permissions=["wbwriter.view_article"]
            ),
        ),
        MenuItem(
            label="Publication",
            endpoint="wbwriter:publication-list",
            permission=ItemPermission(
                method=lambda request: is_internal_user(request.user), permissions=["wbwriter.view_publication"]
            ),
        ),
    ],
)
