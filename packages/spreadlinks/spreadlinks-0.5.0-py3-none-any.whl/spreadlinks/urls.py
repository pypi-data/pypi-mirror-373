# Map URLs to functions for the spreadlinks module.

from django.conf import settings
from django.urls import include, path, re_path

import spreadlinks.views

kwargs = {"root_dir": settings.SPREADLINKS_DIR}
library_detail_paths = [
    path("", spreadlinks.views.library_detail, kwargs, name="library_detail"),
    path(
        "page<int:page>",
        spreadlinks.views.library_detail,
        kwargs,
        name="library_detail",
    ),
]

urlpatterns = [
    path("", spreadlinks.views.library_list, kwargs, name="library_list"),
    path(
        "<library_name>/",
        include(
            [
                path("", include(library_detail_paths)),
                re_path(
                    r"^tags/(?P<urlencoded_keywords>[a-z_0-9+:-]+)",
                    include(library_detail_paths),
                ),
            ]
        ),
    ),
]
