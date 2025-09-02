import logging

from django.db import models

from ob_dj_store.core.stores.gateway.tap import utils

logger = logging.getLogger(__name__)


class TapPaymentManager(models.Manager):
    def create(self, **kwargs):
        # TODO: Add logging to on debug level
        #        if (
        #            "source" not in kwargs
        #            or kwargs.get("source") not in self.model.Sources.values
        #        ):
        #            raise ValueError(f"Invalid source value. {kwargs.get('source')}")
        source = kwargs.pop("source")
        payment = kwargs.get("payment")
        user = kwargs.get("user")
        tap_response = utils.initiate_payment(source, user, payment, payment.currency,)
        kwargs = {**tap_response, **kwargs}
        return super(TapPaymentManager, self).create(**kwargs)
