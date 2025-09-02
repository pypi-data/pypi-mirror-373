"""
Stripe Payment Gateway Managers

This module contains the managers for Stripe payment models.
"""

import logging

from django.db import models

from ob_dj_store.core.stores.gateway.stripe import utils

logger = logging.getLogger(__name__)


class StripePaymentManager(models.Manager):
    """Manager for Stripe payments"""

    def create(self, **kwargs):
        """Create Stripe payment and initiate PaymentIntent"""
        user = kwargs.get("user")
        payment = kwargs.get("payment")

        if not user or not payment:
            raise ValueError("User and payment are required")

        # Initiate Stripe payment
        stripe_response = utils.initiate_stripe_payment(
            user=user, payment=payment, currency_code=payment.currency
        )

        # Merge Stripe response with kwargs
        kwargs.update(stripe_response)

        return super().create(**kwargs)
