from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.functions import Now
from django.utils.translation import gettext_lazy as _
from typing import Self

from amabase.base.models import UserId

class Site(models.Model):
    code = models.CharField(max_length=3, unique=True, help_text="Trigramme du site.")
    name = models.CharField(max_length=30, unique=True)
    num = models.SmallIntegerField(default=100, db_default=100, help_text="Numéro d'ordre du site, notamment dans l'adressage IP des équipements multi-site.")
    # ----------
    comments = models.TextField(blank=True, db_default='')
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET(UserId.DELETED.value), related_name='+', editable=False) # pyright: ignore[reportArgumentType]
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET(UserId.DELETED.value), related_name='+', editable=False) # pyright: ignore[reportArgumentType]

    class Meta:
        ordering = ['num', 'code']
        verbose_name = _("site")

    def __str__(self):
        return self.code
    

class Vendor(models.Model):
    name = models.CharField(max_length=30, unique=True)
    fullname = models.CharField(max_length=50, blank=True, null=True, unique=True)
    public_url = models.CharField(max_length=255, blank=True)
    # ----------
    comments = models.TextField(blank=True, db_default='')
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET(UserId.DELETED.value), related_name='+', editable=False) # pyright: ignore[reportArgumentType]
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET(UserId.DELETED.value), related_name='+', editable=False) # pyright: ignore[reportArgumentType]

    class Meta:
        ordering = ['name']
        verbose_name = _("vendor")

    def __str__(self):
        return self.name
    

class Product(models.Model):
    name = models.CharField(max_length=30, unique=True)
    fullname = models.CharField(max_length=50, blank=True, null=True, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.RESTRICT)
    ref = models.CharField(max_length=30, blank=True, null=True)
    public_url = models.CharField(max_length=255, blank=True)
    # ----------
    comments = models.TextField(blank=True, db_default='')
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET(UserId.DELETED.value), related_name='+', editable=False) # pyright: ignore[reportArgumentType]
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET(UserId.DELETED.value), related_name='+', editable=False) # pyright: ignore[reportArgumentType]

    class Meta:
        unique_together = [
            ('vendor', 'ref'),
        ]
        ordering = ['name']
        verbose_name = _("product")

    def __str__(self):
        return self.name


class Cluster(models.Model):
    """
    A group of host.
    """
    name = models.CharField(max_length=30, unique=True)
    product = models.ForeignKey(Product, blank=True, null=True, on_delete=models.RESTRICT)
    serial = models.CharField(max_length=30, blank=True, null=True)
    # ----------
    comments = models.TextField(blank=True, db_default='')
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET(UserId.DELETED.value), related_name='+', editable=False) # pyright: ignore[reportArgumentType]
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET(UserId.DELETED.value), related_name='+', editable=False) # pyright: ignore[reportArgumentType]

    class Meta:
        unique_together = [
            ('product', 'serial'),
        ]
        ordering = ['name']
        verbose_name = _("cluster")

    def __str__(self):
        return self.name


class HostNature(models.TextChoices):
    SERVER = 'S'
    WORKSTATION = 'W'
    CHASSIS = 'C'
    SWITCH = 'H' # "Hub"
    ROUTER = 'R'
    FIREWALL = 'F'
    

class Host(models.Model):
    name = models.CharField(max_length=30, unique=True) #TODO: warning if more than 15 characters
    slug = models.SlugField(max_length=30, unique=True)
    nature = models.CharField(max_length=1, choices=HostNature.choices, help_text=_("Main nature of the host."))
    site = models.ForeignKey(Site, blank=True, null=True, on_delete=models.RESTRICT)
    location = models.CharField(max_length=30, blank=True, help_text=_("Location of the host within the site."))
    parent: Self = models.ForeignKey('self', blank=True, null=True, on_delete=models.RESTRICT, related_name='child_set', help_text=_("Parent chassis/frame.")) # pyright: ignore[reportAssignmentType]
    cluster = models.ForeignKey(Cluster, blank=True, null=True, on_delete=models.RESTRICT)
    product = models.ForeignKey(Product, blank=True, null=True, on_delete=models.RESTRICT)
    serial = models.CharField(max_length=30, blank=True, null=True)
    management_url = models.CharField(max_length=255, blank=True)
    # ----------
    cpu_cores = models.SmallIntegerField(blank=True, null=True, help_text=_("Number of CPU cores."))
    ram_gib = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True, help_text=_("Random access memory in GiB."))
    #TODO: bios/instance UUID ?
    # ----------
    comments = models.TextField(blank=True, db_default='')
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET(UserId.DELETED.value), related_name='+', editable=False) # pyright: ignore[reportArgumentType]
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET(UserId.DELETED.value), related_name='+', editable=False) # pyright: ignore[reportArgumentType]

    class Meta:
        unique_together = [
            ('product', 'serial'),
        ]
        ordering = ['name']
        verbose_name = _("host")

    def __str__(self):
        return self.name


class HostDisk(models.Model):
    """
    A physical (from the host point of view) disk or volume (group of disks provided e.g. by a RAID controller) in a host.
    """
    host = models.ForeignKey(Site, on_delete=models.RESTRICT)
    pos = models.SmallIntegerField(blank=True, null=True)
    mountpoint = models.CharField(max_length=30, blank=True, null=True)
    # ----------
    product = models.ForeignKey(Product, blank=True, null=True, on_delete=models.RESTRICT)
    serial = models.CharField(max_length=30, blank=True, null=True)
    # ----------
    volume_nature = models.CharField(max_length=30, blank=True)
    parent_volume: Self = models.ForeignKey('self', blank=True, null=True, on_delete=models.RESTRICT, related_name='child_set', help_text=_("Parent volume.")) # pyright: ignore[reportAssignmentType]
    capacity_gib = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True, help_text=_("Capacity in GiB provided to the host."))
    # ----------
    comments = models.TextField(blank=True, db_default='')
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET(UserId.DELETED.value), related_name='+', editable=False) # pyright: ignore[reportArgumentType]
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET(UserId.DELETED.value), related_name='+', editable=False) # pyright: ignore[reportArgumentType]

    class Meta:
        unique_together = [
            ('host', 'pos'),
            ('host', 'mountpoint'),
            ('product', 'serial'),
        ]
        ordering = ['host', 'pos']
        verbose_name = _("disk")

    def __str__(self):
        return f"Disk {self.host}:{self.pos if self.pos is not None else (self.mountpoint if self.mountpoint is not None else '?')}"
