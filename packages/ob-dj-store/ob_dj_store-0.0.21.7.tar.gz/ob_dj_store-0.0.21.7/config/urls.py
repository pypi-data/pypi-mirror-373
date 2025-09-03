from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version="v1",
        basePath="/api/",
        license=openapi.License(name="Privately owned"),
    ),
    public=True,
    urlconf="config.urls",
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path(
        "docs/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-swagger-ui"
    ),
    path("admin/", admin.site.urls),
    path("ecom/", include("ob_dj_store.apis.stores.urls")),
    path("tap/", include("ob_dj_store.apis.tap.urls")),
    path("stripe/", include("ob_dj_store.apis.stripe.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += staticfiles_urlpatterns()
