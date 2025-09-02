from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer
from ipam.models import IPAddress, Prefix, Aggregate
from dcim.models import Device
from netbox_static_routes_communities.models import StaticRoute, Community

# Nested Serializers für Beziehungen
class NestedDeviceSerializer(WritableNestedSerializer):
    class Meta:
        model = Device
        fields = ['id', 'name', 'display']

class NestedPrefixSerializer(WritableNestedSerializer):
    class Meta:
        model = Prefix
        fields = ['id', 'prefix', 'display']

class NestedAggregateSerializer(WritableNestedSerializer):
    class Meta:
        model = Aggregate
        fields = ['id', 'prefix', 'display']

class NestedIPAddressSerializer(WritableNestedSerializer):
    class Meta:
        model = IPAddress
        fields = ['id', 'address', 'display']

class NestedCommunitySerializer(WritableNestedSerializer):
    class Meta:
        model = Community
        fields = ['id', 'community', 'display']

# Custom Field für den GenericForeignKey "target"
class TargetField(serializers.Field):
    """
    Serialisiert GenericForeignKey target auf Prefix oder Aggregate
    """
    def to_representation(self, obj):
        if obj is None:
            return None
        if isinstance(obj, Prefix):
            return NestedPrefixSerializer(obj, context=self.context).data
        elif isinstance(obj, Aggregate):
            return NestedAggregateSerializer(obj, context=self.context).data
        return str(obj)

class StaticRouteSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_static_routes_communities-api:staticroute-detail'
    )

    device = NestedDeviceSerializer()
    # Mapping von target auf prefix für die API
    prefix = TargetField(source='target')
    ip_address = NestedIPAddressSerializer()
    discard = serializers.BooleanField()
    communities = NestedCommunitySerializer(many=True)

    class Meta:
        model = StaticRoute
        fields = (
            'id', 'url', 'display', 'device', 'prefix', 'ip_address',
            'discard', 'communities', 'comments', 'tags', 'custom_fields',
            'created', 'last_updated',
        )

class CommunitySerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_static_routes_communities-api:community-detail'
    )

    class Meta:
        model = Community
        fields = (
            'id', 'url', 'display', 'community', 'description',
            'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        )
