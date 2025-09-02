from wbcore.menus import ItemPermission, Menu, MenuItem

WIKI_MENU_ITEM = MenuItem(
    label="WIKI",
    endpoint="wbwiki:wikiarticle-list",
    add=MenuItem(
        label="Create a wiki article",
        endpoint="wbwiki:wikiarticle-list",
        permission=ItemPermission(
            permissions=["wbwiki.create_wikiarticle"],
        ),
    ),
    permission=ItemPermission(
        permissions=["wbwiki.view_wikiarticle"],
    ),
)

WIKI_MENU = Menu(
    label="WIKI",
    items=[WIKI_MENU_ITEM],
)
