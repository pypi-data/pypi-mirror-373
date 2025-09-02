from __future__ import annotations

from django.contrib.gis.db.models import fields as gis_fields
from django.db.models import fields as std_fields

from amabase.conf import settings

if settings.USE_GIS:
    class PositionField(gis_fields.PointField):
        pass

else:
    class PositionField(std_fields.CharField):
        def __init__(self, **kwargs):
            if not 'max_length' in kwargs:
                kwargs['max_length'] = 21 # lat,lng
            super().__init__(**kwargs)
