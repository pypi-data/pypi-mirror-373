from amabase.django.admin import register, unregister
from django.contrib.auth.models import Group as BaseGroup
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin

from amabase.base.models import Group, User

unregister(BaseGroup)


@register(Group)
class GroupAdmin(BaseGroupAdmin):
    pass


@register(User)
class UserAdmin(BaseUserAdmin):
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets[1][1]['fields'] = (*fieldsets[1][1]['fields'], 'gpg_keyid', 'ssh_pubkey', 'comments')
        return fieldsets
