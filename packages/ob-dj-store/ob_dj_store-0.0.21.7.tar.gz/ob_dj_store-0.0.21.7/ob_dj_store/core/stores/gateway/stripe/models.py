"""
Stripe Payment Gateway Models

This module contains the models for Stripe payment integration,
mirroring the structure of the TAP payment gateway.
"""

import logging

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from ob_dj_store.core.stores.gateway.stripe.managers import StripePaymentManager

logger = logging.getLogger(__name__)


class StripePayment(models.Model):
    """StripePayment captures the payment from Stripe"""

    class Status(models.TextChoices):
        REQUIRES_PAYMENT_METHOD = (
            "requires_payment_method",
            _("Requires Payment Method"),
        )
        REQUIRES_CONFIRMATION = "requires_confirmation", _("Requires Confirmation")
        REQUIRES_ACTION = "requires_action", _("Requires Action")
        PROCESSING = "processing", _("Processing")
        REQUIRES_CAPTURE = "requires_capture", _("Requires Capture")
        CANCELED = "canceled", _("Canceled")
        SUCCEEDED = "succeeded", _("Succeeded")

    class Sources(models.TextChoices):
        CARD = "card", _("Credit/Debit Card")
        APPLE_PAY = "apple_pay", _("Apple Pay")
        GOOGLE_PAY = "google_pay", _("Google Pay")
        ACH_DEBIT = "ach_debit", _("ACH Bank Transfer")
        KLARNA = "klarna", _("Klarna")
        AFTERPAY = "afterpay_clearpay", _("Afterpay")

    # Core fields
    payment = models.OneToOneField(
        "stores.Payment",
        on_delete=models.CASCADE,
        related_name="stripe_payment",
        help_text=_("Reference to local payment transaction"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text=_("User who initiated the payment"),
    )

    # Stripe specific fields
    payment_intent_id = models.CharField(
        max_length=250,
        unique=True,
        db_index=True,
        help_text=_("Stripe PaymentIntent ID"),
    )
    client_secret = models.CharField(
        max_length=250, help_text=_("Client secret for frontend confirmation")
    )
    status = models.CharField(
        max_length=50, choices=Status.choices, default=Status.REQUIRES_PAYMENT_METHOD
    )
    source = models.CharField(
        max_length=50, choices=Sources.choices, default=Sources.CARD
    )

    # Response data
    init_response = models.JSONField(
        help_text=_("Initial PaymentIntent response from Stripe"), null=True, blank=True
    )
    webhook_response = models.JSONField(
        help_text=_("Final webhook response from Stripe"), null=True, blank=True
    )

    # Metadata
    langid = models.CharField(
        max_length=10, default="EN", help_text=_("Language preference")
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = StripePaymentManager()

    class Meta:
        verbose_name = _("Stripe Payment")
        verbose_name_plural = _("Stripe Payments")
        ordering = ["-created_at"]

    def __str__(self):
        return f"StripePayment {self.payment_intent_id}"

    @property
    def amount(self):
        """Return payment amount in dollars"""
        return self.payment.total_payment

    @property
    def amount_cents(self):
        """Return payment amount in cents for Stripe"""
        return int(self.amount * 100)

    @property
    def currency(self):
        """Get currency from payment"""
        return self.payment.currency.lower()

    @property
    def payment_url(self):
        """Return client secret for frontend processing"""
        return self.client_secret

    def webhook_update(self, stripe_event):
        """Update payment based on Stripe webhook"""
        payment_intent = stripe_event["data"]["object"]

        # Update status and webhook response
        old_status = self.status
        self.status = payment_intent["status"]
        self.webhook_response = payment_intent
        self.save()

        # Mark transaction based on new status
        self.mark_transaction()

        logger.info(
            f"Stripe webhook updated PaymentIntent {self.payment_intent_id}: {old_status} -> {self.status}"
        )

    def mark_transaction(self):
        """Mark the associated payment based on Stripe status"""
        if self.status == self.Status.SUCCEEDED:
            self.payment.mark_paid()
        elif self.status in [self.Status.CANCELED]:
            error_message = self.webhook_response.get("last_payment_error", {}).get(
                "message", "Payment failed"
            )
            self.payment.mark_failed(error_message)


class StripeCustomer(models.Model):
    """Stripe customer mapping"""

    customer = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="stripe_customer",
    )
    stripe_customer_id = models.CharField(max_length=200, unique=True, db_index=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True, null=True)
    phone_number = PhoneNumberField(unique=True, null=True)

    # Store original Stripe response
    init_data = models.JSONField()

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Stripe Customer")
        verbose_name_plural = _("Stripe Customers")

    def __str__(self):
        return f"{self.email} | {self.stripe_customer_id}"
