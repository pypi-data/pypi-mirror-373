from django.conf.urls import include
from django.urls import path
from rest_framework.routers import SimpleRouter

from ob_dj_store.apis.tap.views import TapPaymentViewSet

app_name = "tap_gateway"

router = SimpleRouter(trailing_slash=False)

router.register(r"", TapPaymentViewSet, basename="taptransaction")


urlpatterns = [
    path("", include(router.urls)),
]
