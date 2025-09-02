from dcim.models import Device
from ipam.models import Prefix, Aggregate, IPAddress
from .models import StaticRoute, Community
from django.contrib.contenttypes.models import ContentType
from django_filters import NumberFilter, ModelChoiceFilter
from netbox.filtersets import NetBoxModelFilterSet

class StaticRouteFilterSet(NetBoxModelFilterSet):
    prefix = ModelChoiceFilter(
        method='filter_prefix',
        queryset=Prefix.objects.all()
    )
    aggregate = ModelChoiceFilter(
        method='filter_aggregate',
        queryset=Aggregate.objects.all()
    )
    device = ModelChoiceFilter(queryset=Device.objects.all())
    ip_address = ModelChoiceFilter(queryset=IPAddress.objects.all())
    discard = NumberFilter(field_name='discard')
    communities = ModelChoiceFilter(queryset=Community.objects.all())

    class Meta:
        model = StaticRoute
        fields = ()

    def filter_prefix(self, queryset, name, value):
        ct = ContentType.objects.get_for_model(Prefix)
        return queryset.filter(target_type=ct, target_id=value.id)

    def filter_aggregate(self, queryset, name, value):
        ct = ContentType.objects.get_for_model(Aggregate)
        return queryset.filter(target_type=ct, target_id=value.id)

    def search(self, queryset, name, value):
        return queryset.filter(comments__icontains=value)

class CommunityFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = Community
        fields = ("id", "community", "description",)

    def search(self, queryset, name, value):
        return queryset.filter(comments__icontains=value)
