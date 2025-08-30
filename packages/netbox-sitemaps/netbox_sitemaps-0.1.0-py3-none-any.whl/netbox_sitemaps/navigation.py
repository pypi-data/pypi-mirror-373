from netbox.plugins import PluginMenuButton, PluginMenuItem


plugin_buttons = [
    PluginMenuButton(
        link="plugins:netbox_sitemaps:sitemaps_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
    )
]

menu_items = (
    PluginMenuItem(
        link="plugins:netbox_sitemaps:sitemaps_list",
        link_text="Sitemaps",
        buttons=plugin_buttons,
    ),
)
