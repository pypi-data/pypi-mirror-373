from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from netbox.models import NetBoxModel
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

class StaticRoute(NetBoxModel):
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('Device'),
    )

    target_type = models.ForeignKey(
        ContentType,
        limit_choices_to={'model__in': ('prefix', 'aggregate')},
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_('Target type'),
    )
    target_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Target ID'),
    )
    target = GenericForeignKey('target_type', 'target_id')

    ip_address = models.ForeignKey(
        to='ipam.IPAddress',
        on_delete=models.PROTECT,
        related_name='+',
        null=True,
        blank=True,
        verbose_name=_('Next-Hop'),
    )

    discard = models.BooleanField(
        default=False,
        verbose_name='Discard route',
        help_text='Discard the route instead of forwarding to a next-hop.'
    )

    communities = models.ManyToManyField(
        to='Community',
        related_name='static_routes',
        blank=True,
        verbose_name=_('Communities'),
    )

    comments = models.TextField(
        blank=True,
        verbose_name=_('Comments'),
    )

    prerequisite_models = (
        'dcim.Device',
        'ipam.Prefix',
        'ipam.Aggregate',
        'ipam.IPAddress',
    )

    class Meta:
        ordering = ['device']
        constraints = [
            models.UniqueConstraint(
                fields=['device', 'target_type', 'target_id'],
                name='unique_device_target'
            )
        ]

    def __str__(self):
        return f"{self.target}"

    def get_absolute_url(self):
        return reverse('plugins:netbox_static_routes_communities:staticroute', args=[self.pk])

class Community(NetBoxModel):
    community = models.TextField(
        verbose_name=_('Community'),
    )

    description = models.TextField(
        blank=True,
        verbose_name=_('Description'),
    )

    comments = models.TextField(
        blank=True,
        verbose_name=_('Comments'),
    )

    class Meta:
        ordering = ['community',]

    def __str__(self):
        return str(self.community)

    def get_absolute_url(self):
        return reverse('plugins:netbox_static_routes_communities:community', args=[self.pk])
