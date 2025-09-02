from netbox.views import generic
from . import filtersets, forms, models, tables, import_forms
from utilities.views import ViewTab, register_model_view
from dcim.models import Device
from django.shortcuts import render, get_object_or_404
from .models import StaticRoute, Community
from .tables import StaticRouteTable, CommunityTable
from django.views import View
from django.contrib.auth.mixins import PermissionRequiredMixin

class StaticRouteView(generic.ObjectView):
    queryset = models.StaticRoute.objects.all()
    table = tables.StaticRoute

class StaticRouteListView(generic.ObjectListView):
    queryset = models.StaticRoute.objects.all()
    table = tables.StaticRouteTable
    filterset = filtersets.StaticRouteFilterSet
    filterset_form = forms.StaticRouteFilterForm

class StaticRouteEditView(generic.ObjectEditView):
    queryset = StaticRoute.objects.all()
    form = forms.StaticRouteForm

class StaticRouteDeleteView(generic.ObjectDeleteView):
    queryset = models.StaticRoute.objects.all()

class StaticRouteImportView(generic.BulkImportView):
    queryset = models.StaticRoute.objects.all()
    model_form = import_forms.StaticRouteImportForm

@register_model_view(Device, name="static-routes", path="static-routes")
class DeviceStaticRouteView(PermissionRequiredMixin, View):
    permission_required = "netbox_static_routes_communities.view_staticroute"
    template_name = "netbox_static_routes_communities/device_static_routes.html"
    tab = ViewTab(
        label="Static Routes",
        badge=lambda obj: StaticRoute.objects.filter(device=obj).count(),
        permission="netbox_static_routes_communities.view_staticroute",
        visible=lambda obj: StaticRoute.objects.filter(device=obj).exists(),
    )

    def get(self, request, pk):
        device = get_object_or_404(Device, pk=pk)
        routes = StaticRoute.objects.filter(device=device)
        table = StaticRouteTable(routes, user=request.user)

        return render(
            request,
            self.template_name,
            {
                "object": device,
                "routes_table": table,
                "tab": self.tab,
            },
        )

class CommunityView(generic.ObjectView):
    queryset = models.Community.objects.all()
    table = tables.Community

class CommunityListView(generic.ObjectListView):
    queryset = models.Community.objects.all()
    table = tables.CommunityTable
    filterset = filtersets.CommunityFilterSet
    filterset_form = forms.CommunityFilterForm

class CommunityEditView(generic.ObjectEditView):
    queryset = Community.objects.all()
    form = forms.CommunityForm

class CommunityDeleteView(generic.ObjectDeleteView):
    queryset = models.Community.objects.all()