from netbox.api.viewsets import NetBoxModelViewSet

from .. import filtersets, models
from .serializers import StaticRouteSerializer, CommunitySerializer

class StaticRouteViewSet(NetBoxModelViewSet):
    queryset = models.StaticRoute.objects.prefetch_related(
        'device', 'prefix', 'ip_address', 'tags'
    )
    serializer_class = StaticRouteSerializer
    
class CommunityViewSet(NetBoxModelViewSet):
    queryset = models.Community.objects.prefetch_related(
        'tags'
    )
    serializer_class = CommunitySerializer
    