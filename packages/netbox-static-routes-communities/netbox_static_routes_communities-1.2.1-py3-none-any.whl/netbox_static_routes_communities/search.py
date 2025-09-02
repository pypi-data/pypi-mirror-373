from netbox.search import SearchIndex, register_search
from .models import StaticRoute, Community

@register_search
class StaticRouteIndex(SearchIndex):
    model = StaticRoute
    fields = (
        ('target', 200),
        ('comments', 5000),
    )

@register_search
class CommunityIndex(SearchIndex):
    model = Community
    fields = (
        ('community', 200),
        ('description', 500),
        ('comments', 5000),
    )