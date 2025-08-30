"""Top-level package for NetBox Sitemaps Plugin."""

__author__ = """Lars Däschner"""
__email__ = "contact@ldaeschner.de"
__version__ = "0.1.0"


from netbox.plugins import PluginConfig


class SitemapsConfig(PluginConfig):
    name = "netbox_sitemaps"
    verbose_name = "NetBox Sitemaps Plugin"
    description = "NetBox plugin to display sites on a map."
    version = "version"
    base_url = "netbox_sitemaps"


config = SitemapsConfig
