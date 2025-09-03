def classFactory(iface):
    from .oqtopus_plugin import OqtopusPlugin

    return OqtopusPlugin(iface)
