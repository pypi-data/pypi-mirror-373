from __future__ import annotations

from django.contrib.admin import ModelAdmin as BaseModelAdmin, StackedInline, TabularInline, display, register, site
from django.db.models import Model, TextField, CharField
from django.forms import ModelForm
from django.http import HttpRequest


class ModelAdmin(BaseModelAdmin):
    def save_model(self, request: HttpRequest, obj: Model, form: ModelForm, change: bool):
        # Change blank to null depending on the configuration of the field (usefull for example for nullable unique fields)
        for field in obj._meta.get_fields():
            if isinstance(field, (TextField, CharField)):
                if field.blank and field.null:
                    if getattr(obj, field.attname) == '':
                        setattr(obj, field.attname, None)

        # Set user fields
        if hasattr(obj, 'updated_by'):
            setattr(obj, 'updated_by', request.user)
        if not change and hasattr(obj, 'created_by'):
            setattr(obj, 'created_by', request.user)
                
        super().save_model(request, obj, form, change)


unregister = site.unregister


__all__ = ('ModelAdmin',
           # Shortcuts
           'TabularInline', 'StackedInline', 'display', 'register', 'unregister')
