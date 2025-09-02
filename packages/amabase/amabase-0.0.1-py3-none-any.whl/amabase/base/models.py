from django.db import models
from django.contrib.auth.models import AbstractUser, Group as BaseGroup
from django.utils.translation import gettext_lazy as _


class Group(BaseGroup):
    # ----------
    comments = models.TextField(blank=True, db_default='')


class User(AbstractUser):
    gpg_keyid = models.CharField(max_length=255, blank=True, verbose_name=_("GPG key identifier"))
    ssh_pubkey = models.TextField(blank=True, verbose_name=_("SSH public key"))
    # ----------
    comments = models.TextField(blank=True, db_default='')

    # ----- Relations -----    
    groups = models.ManyToManyField(Group, verbose_name=_("groups"), blank=True, help_text=_("The groups this user belongs to. A user will get all permissions granted to each of their groups."), related_name="user_set", related_query_name="user")


class UserId(models.IntegerChoices):
    DELETED = -1

    SEEDER = -2
