from netbox.plugins import PluginConfig

class NetboxStaticRoutesConfig(PluginConfig):
    name = 'netbox_static_routes_communities'
    verbose_name = 'Netbox Static Routes'
    description = 'Display static routes in Netbox'
    version = '1.2.1'
    min_version = '4.3.0'
    base_url = 'static-routes'
    author = 'Marlon Sieker'
    author_email = 'Marlon.Sieker@tkrz.de'

config = NetboxStaticRoutesConfig
