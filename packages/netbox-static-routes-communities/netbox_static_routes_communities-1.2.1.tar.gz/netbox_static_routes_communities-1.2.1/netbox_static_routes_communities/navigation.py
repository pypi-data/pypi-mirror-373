from netbox.plugins import PluginMenuItem, PluginMenuButton

staticroute_buttons = [
    PluginMenuButton(
        link='plugins:netbox_static_routes_communities:staticroute_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
    ),
    PluginMenuButton(
        link='plugins:netbox_static_routes_communities:staticroute_import',
        title='Import',
        icon_class='mdi mdi-upload',
    )
]

community_buttons = [
    PluginMenuButton(
        link='plugins:netbox_static_routes_communities:community_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
    )
]

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_static_routes_communities:staticroute_list',
        link_text='Static Routes',
        buttons=staticroute_buttons
    ),
    PluginMenuItem(
        link='plugins:netbox_static_routes_communities:community_list',
        link_text='Communities',
        buttons=community_buttons
    ),
)
