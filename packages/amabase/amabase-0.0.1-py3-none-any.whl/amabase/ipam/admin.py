from amabase.django.admin import ModelAdmin, register
from amabase.ipam.models import IPv4Address, Range


@register(Range)
class RangeAdmin(ModelAdmin):
    list_display = ['name', 'vlan', 'ipv4_begin', 'ipv4_end', 'ipv4_subnet_length', 'ipv4_subnet_mask']


@register(IPv4Address)
class IPv4AddressAdmin(ModelAdmin):
    list_display = ['address', 'range', 'nature', 'host']
