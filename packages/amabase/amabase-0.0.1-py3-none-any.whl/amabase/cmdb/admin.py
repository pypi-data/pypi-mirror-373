from __future__ import annotations

from urllib.parse import urlparse

from django.utils.safestring import mark_safe

from amabase.cmdb.models import Cluster, Host, Product, Site, Vendor
from amabase.django.admin import ModelAdmin, register


@register(Site)
class SiteAdmin(ModelAdmin):
    list_display = ['code', 'name', 'num']
    search_fields = ['code', 'name']


@register(Vendor)
class VendorAdmin(ModelAdmin):
    list_display = ['name', 'fullname', 'public_link']
    search_fields = ['name', 'fullname']

    def public_link(self, obj: Vendor):
        if not obj.public_url:
            return None
        parts = urlparse(obj.public_url)
        return mark_safe(f'<a href="{obj.public_url}" target="_blank">{parts.netloc}</a>')


@register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ['name', 'fullname', 'vendor', 'ref', 'public_link']
    search_fields = ['name', 'fullname']

    def public_link(self, obj: Product):
        if not obj.public_url:
            return None
        parts = urlparse(obj.public_url)
        return mark_safe(f'<a href="{obj.public_url}" target="_blank">{parts.netloc}</a>')


@register(Cluster)
class ClusterAdmin(ModelAdmin):
    list_display = ['name', 'product', 'serial']
    search_fields = ['name']


@register(Host)
class HostAdmin(ModelAdmin):
    list_display = ['name', 'nature', 'site', 'location', 'parent', 'cluster', 'product', 'serial', 'management_link']
    prepopulated_fields = {'slug': ['name']}
    search_fields = ['name', 'site', 'location', 'serial']

    def management_link(self, obj: Host):
        if not obj.management_url:
            return None
        parts = urlparse(obj.management_url)
        return mark_safe(f'<a href="{obj.management_url}" target="_blank">{parts.netloc}</a>')
