from typing import Sequence
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.functions import Now
from django.utils.translation import gettext_lazy as _

from amabase.base.models import UserId
from amabase.cmdb.models import Host

class Range(models.Model):
    name = models.CharField(max_length=50, unique=True)
    vlan = models.SmallIntegerField(blank=True, null=True, unique=True)
    ipv4_begin = models.GenericIPAddressField(protocol='IPv4', blank=True, null=True, db_default='')
    ipv4_end = models.GenericIPAddressField(protocol='IPv4', blank=True, null=True, db_default='')
    # ----------
    comments = models.TextField(blank=True, db_default='')
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET(UserId.DELETED.value), related_name='+', editable=False) # pyright: ignore[reportArgumentType]
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET(UserId.DELETED.value), related_name='+', editable=False) # pyright: ignore[reportArgumentType]

    class Meta:
        ordering = ['name']
        verbose_name = _("range")
        verbose_name_plural = _("ranges")

    def __str__(self):
        return self.name
    
    @property
    def ipv4_subnet_length(self) -> int:
        #TODO: display subnet net if it is one, and auto create network and broadcast address if they are not already created
        return 0 #TODO
    
    @property
    def ipv4_subnet_mask(self) -> str:
        #TODO: display subnet net if it is one, and auto create network and broadcast address if they are not already created
        return 'TODO' #TODO


class AddressNature(models.TextChoices):
    APPLICATION = 'A'
    """ Application provided by a host. """

    MANAGEMENT = 'M'
    """ Management/ILO port. """
    
    NETWORK = 'N'
    """ Network address. """
    
    BROADCAST = 'B'
    """ Network broadcast address. """
    
    GATEWAY = 'G'
    """ Network gateway address. """

    RESERVED = 'R'
    """ Reserved for a non-specified usage. """

    USABLE = 'U'
    """ The address may be used. """


def on_address_delete(collector, field, sub_objs: Sequence[models.Model], using: str):
    #TODO: set name of host in comments
    print("on_address_delete", collector, field, sub_objs, using)
    print("field", type(field), type(field.model), field.model)
    return None


class IPv4Address(models.Model):
    address = models.GenericIPAddressField(protocol='IPv4', unique=True)
    range = models.ForeignKey(Range,  on_delete=models.RESTRICT) # TODO: auto detection?
    nature = models.CharField(max_length=1, choices=AddressNature, default=AddressNature.RESERVED)
    host = models.ForeignKey(Host, blank=True, null=True, on_delete=models.SET(on_address_delete)) # pyright: ignore[reportCallIssue, reportArgumentType]
    # ----------
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET(UserId.DELETED.value), related_name='+', editable=False) # pyright: ignore[reportArgumentType]
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())
    updated_by = models.ForeignKey(get_user_model(), on_delete=models.SET(UserId.DELETED.value), related_name='+', editable=False) # pyright: ignore[reportArgumentType]

    class Meta:
        ordering = ['address']
        verbose_name = _("IPv4 address")
        verbose_name_plural = _("IPv4 addresses")

    def __str__(self):
        return self.address
