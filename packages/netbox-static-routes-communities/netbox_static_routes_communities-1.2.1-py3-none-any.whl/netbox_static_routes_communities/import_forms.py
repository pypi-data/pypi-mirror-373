from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from dcim.models import Device
from ipam.models import Prefix, Aggregate, IPAddress
from netbox.forms import NetBoxModelImportForm
from utilities.forms.fields import (
    CSVModelChoiceField, CSVModelMultipleChoiceField
)

from .models import StaticRoute, Community

class StaticRouteImportForm(NetBoxModelImportForm):
    device = CSVModelChoiceField(
        label=_('Device'),
        queryset=Device.objects.all(),
        to_field_name='name',
        help_text=_('Device on which the static route is configured')
    )

    prefix = CSVModelChoiceField(
        label=_('Prefix'),
        queryset=Prefix.objects.all(),
        to_field_name='prefix',
        required=False,
        help_text=_('Destination prefix (e.g. 192.168.0.0/16)')
    )

    aggregate = CSVModelChoiceField(
        label=_('Aggregate'),
        queryset=Aggregate.objects.all(),
        to_field_name='prefix',
        required=False,
        help_text=_('Destination aggregate (e.g. 10.0.0.0/8)')
    )

    ip_address = CSVModelChoiceField(
        label=_('Next-Hop'),
        queryset=IPAddress.objects.all(),
        required=False,
        to_field_name='address',
        help_text=_('Next-hop IP address (leave blank if discard)')
    )

    discard = forms.BooleanField(
        required=False,
        label=_('Discard route'),
        help_text=_('Discard the route instead of forwarding to a next-hop')
    )

    communities = CSVModelMultipleChoiceField(
        queryset=Community.objects.all(),
        required=False,
        to_field_name='community',
        help_text=_('Communities attached to the route')
    )

    class Meta:
        model = StaticRoute
        fields = ('device', 'prefix', 'aggregate', 'ip_address', 'discard', 'communities', 'comments', 'tags')

    def clean(self):
        super().clean()

        prefix = self.cleaned_data.get("prefix")
        aggregate = self.cleaned_data.get("aggregate")

        if prefix and aggregate:
            raise forms.ValidationError("Please choose either a Prefix OR an Aggregate, not both.")
        if not prefix and not aggregate:
            raise forms.ValidationError("You must specify a Prefix or an Aggregate.")

        self.cleaned_data["target"] = prefix or aggregate
        return self.cleaned_data

    def save(self, *args, **kwargs):
        target = self.cleaned_data.get("target")
        discard = self.cleaned_data.get("discard")

        if discard:
            self.instance.ip_address = None

        if target is not None:
            self.instance.target = target

        return super().save(*args, **kwargs)