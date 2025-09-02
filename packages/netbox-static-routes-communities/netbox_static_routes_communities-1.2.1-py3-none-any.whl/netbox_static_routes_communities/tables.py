import django_tables2 as tables

from netbox.tables import NetBoxTable, ChoiceFieldColumn
from .models import StaticRoute, Community

class StaticRouteTable(NetBoxTable):
    id = tables.Column(
        linkify=True
    )
    device = tables.Column(
        linkify=True
    )

    prefix = tables.Column(
        accessor='target', linkify=True
    )

    ip_address = tables.Column(
        linkify=True
    )

    class Meta(NetBoxTable.Meta):
        model = StaticRoute
        fields = ('pk', 'id', 'device', 'prefix', 'ip_address', 'discard', 'comments')
        default_columns = ('id', 'device', 'prefix', 'ip_address', 'discard')

class CommunityTable(NetBoxTable):
    community = tables.Column(
        linkify=True
    )

    class Meta(NetBoxTable.Meta):
        model = Community
        fields = ('pk', 'id', 'community', 'description', 'comments')
        default_columns = ('community', 'description')