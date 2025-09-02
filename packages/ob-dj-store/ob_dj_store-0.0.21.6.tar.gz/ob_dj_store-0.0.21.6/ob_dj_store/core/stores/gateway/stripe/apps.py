from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StripeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ob_dj_store.core.stores.gateway.stripe"
    verbose_name = _("Gateway: Stripe")
    label = "stripe"
