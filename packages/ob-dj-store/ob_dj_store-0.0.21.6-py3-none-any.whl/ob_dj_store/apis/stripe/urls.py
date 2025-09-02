from django.conf.urls import include
from django.urls import path
from rest_framework.routers import SimpleRouter

from ob_dj_store.apis.stripe.views import StripePaymentViewSet, StripeWebhookViewSet

app_name = "stripe_gateway"

router = SimpleRouter(trailing_slash=False)

# Payment management endpoints
router.register(r"payments", StripePaymentViewSet, basename="stripe-payment")

# Webhook endpoints
router.register(r"webhook", StripeWebhookViewSet, basename="stripe-webhook")

urlpatterns = [
    # Direct webhook URL for easier access from Stripe
    path(
        "callback/",
        StripeWebhookViewSet.as_view({"post": "callback"}),
        name="webhook-callback",
    ),
    path("", include(router.urls)),
]
