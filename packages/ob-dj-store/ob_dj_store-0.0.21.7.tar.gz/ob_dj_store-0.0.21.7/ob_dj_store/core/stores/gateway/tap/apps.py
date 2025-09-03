from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GatewayTapConfig(AppConfig):
    name = "ob_dj_store.core.stores.gateway.tap"
    verbose_name = _("Gateway: Tap")
