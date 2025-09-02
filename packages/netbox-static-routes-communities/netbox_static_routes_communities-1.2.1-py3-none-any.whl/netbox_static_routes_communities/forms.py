from django import forms
from ipam.models import Prefix, IPAddress, Aggregate
from dcim.models import Device
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from .models import StaticRoute, Community
from utilities.forms.fields import CommentField, DynamicModelChoiceField, DynamicModelMultipleChoiceField
from utilities.forms.rendering import FieldSet, TabbedGroups
from django.contrib.contenttypes.models import ContentType

class StaticRouteForm(NetBoxModelForm):
    comments = CommentField()

    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        label='Device'
    )
    prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label='Prefix'
    )
    aggregate = DynamicModelChoiceField(
        queryset=Aggregate.objects.all(),
        required=False,
        label='Aggregate'
    )
    ip_address = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label='Next-Hop'
    )
    discard = forms.BooleanField(
        required=False,
        label='Discard route'
    )
    communities = DynamicModelMultipleChoiceField(
        queryset=Community.objects.all(),
        required=False,
        label='Communities'
    )

    fieldsets = (
        FieldSet('device', name='Static Route'),
        FieldSet(
            TabbedGroups(
                FieldSet('prefix', name='Prefix'),
                FieldSet('aggregate', name='Aggregate'),
            ),
            name='Network'
        ),
        FieldSet('ip_address', 'discard', name='Next Hop'),
        FieldSet('communities', name='Communities'),
    )

    class Meta:
        model = StaticRoute
        fields = ('device', 'prefix', 'aggregate', 'ip_address', 'discard', 'communities', 'comments', 'tags')

    def clean(self):
        super().clean()

        prefix = self.cleaned_data.get('prefix')
        aggregate = self.cleaned_data.get('aggregate')
        discard = self.cleaned_data.get('discard')
        ip_address = self.cleaned_data.get('ip_address')

        if prefix and aggregate:
            self.add_error('aggregate', 'Please choose either a Prefix OR an Aggregate, not both.')
        if not prefix and not aggregate:
            self.add_error('prefix', 'You must specify a Prefix or an Aggregate.')

        if discard and ip_address:
            self.add_error('ip_address', 'Cannot set both Next-Hop and Discard route.')
        elif not discard and not ip_address:
            self.add_error('ip_address', 'You must specify a Next-Hop or check "Discard route".')

        if discard:
            self.cleaned_data['ip_address'] = None

        if prefix:
            self.instance.target = prefix
        elif aggregate:
            self.instance.target = aggregate

class StaticRouteFilterForm(NetBoxModelFilterSetForm):
    model = StaticRoute

    device = forms.ModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False
    )

    prefix = forms.ModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False
    )

    aggregate = forms.ModelMultipleChoiceField(
        queryset=Aggregate.objects.all(),
        required=False
    )

    ip_address = forms.ModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label='Next-Hop'
    )

    discard = forms.BooleanField(
        required=False,
        label='Discard route'
    )

    community = forms.ModelMultipleChoiceField(
        queryset=Community.objects.all(),
        required=False,
        label='Communities'
    )

class CommunityForm(NetBoxModelForm):
    community = forms.CharField()
    
    description = forms.CharField(
        required=False,
    )

    comments = CommentField()

    class Meta:
        model = Community
        fields = ('community', 'description', 'comments', 'tags')

class CommunityFilterForm(NetBoxModelFilterSetForm):
    model = Community
