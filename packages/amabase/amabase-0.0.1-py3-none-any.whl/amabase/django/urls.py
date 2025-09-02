from __future__ import annotations

import re

from django.contrib import admin
from django.templatetags.static import static
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.views.static import serve

from amabase.conf import settings

admin.site.site_title = settings.SITE_TITLE
admin.site.site_header = settings.SITE_TITLE
admin.site.index_title = settings.SITE_INDEX_HEADER

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url=settings.FAVICON_URL if '://' in settings.FAVICON_URL or settings.FAVICON_URL.startswith('/') else static(settings.FAVICON_URL))),
    path('__debug__/', include('debug_toolbar.urls')),    
    path('', admin.site.urls),
]

if not settings.DEBUG:
    urlpatterns += [
        re_path(r"^%s(?P<path>.*)$" % re.escape(settings.MEDIA_URL), serve, kwargs={'document_root': settings.MEDIA_ROOT}),
        re_path(r"^%s(?P<path>.*)$" % re.escape(settings.STATIC_URL), serve, kwargs={'document_root': settings.STATIC_ROOT}),
    ]
