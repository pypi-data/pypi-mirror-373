from django.utils.translation import gettext_lazy as _
from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

NEWS_MENUITEM = MenuItem(
    label=_("News"),
    endpoint="wbnews:news-list",
    permission=ItemPermission(permissions=["wbnews.view_news"]),
)
NEWSRELATIONSHIP_MENUITEM = MenuItem(
    label=_("News Relationships"),
    endpoint="wbnews:newsrelationship-list",
    permission=ItemPermission(permissions=["wbnews.view_news"]),
)

NEWSSOURCE_MENUITEM = MenuItem(
    label=_("Sources"),
    endpoint="wbnews:source-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbnews.view_newssource"]
    ),
    add=MenuItem(
        label=_("Create Source"),
        endpoint="wbnews:source-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user), permissions=["wbnews.add_newssource"]
        ),
    ),
)
