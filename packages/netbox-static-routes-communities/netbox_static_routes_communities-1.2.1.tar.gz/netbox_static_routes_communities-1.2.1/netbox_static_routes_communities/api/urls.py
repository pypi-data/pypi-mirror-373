from netbox.api.routers import NetBoxRouter
from . import views

app_name = 'netbox_static_routes_communities'

router = NetBoxRouter()
router.register('static-routes', views.StaticRouteViewSet)
router.register('community', views.CommunityViewSet)

urlpatterns = router.urls
