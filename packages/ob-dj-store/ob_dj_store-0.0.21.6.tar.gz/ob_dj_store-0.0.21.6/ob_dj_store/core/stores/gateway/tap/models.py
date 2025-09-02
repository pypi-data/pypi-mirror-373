import logging

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from ob_dj_store.core.stores.gateway.tap.managers import TapPaymentManager

logger = logging.getLogger(__name__)


class TapPayment(models.Model):
    """TapPayment captures the payment from Tap"""

    class Status(models.TextChoices):
        INITIATED = "INITIATED"
        IN_PROGRESS = "IN_PROGRESS"
        ABANDONED = "ABANDONED"
        CANCELLED = "CANCELLED"
        FAILED = "FAILED"
        DECLINED = "DECLINED"
        RESTRICTED = "RESTRICTED"
        CAPTURED = "CAPTURED"
        VOID = "VOID"
        TIMEDOUT = "TIMEDOUT"
        UNKNOWN = "UNKNOWN"

    class Sources(models.TextChoices):
        CREDIT_CARD = "src_card", _("Credit Card")
        KNET = "src_kw.knet", _("KNet")
        APPLE_PAY = "apple_pay", _("Apple pay")
        GOOGLE_PAY = "google_pay", _("Google pay")
        ALL = "src_all", _("All")

    status = models.CharField(max_length=100, choices=Status.choices)
    source = models.CharField(max_length=100, choices=Sources.choices)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text=_(
            "Captured the User ID for both registered "
            "users and Guests (Every guest user has a user_id assigned by device_id)"
        ),
    )
    langid = models.CharField(
        max_length=10,
        help_text=_(
            "Capture language for debugging & analytical only purposes (ARA for Arabic & ENG for English)"
        ),
    )
    payment = models.OneToOneField(
        "stores.Payment",
        on_delete=models.CASCADE,
        related_name="tap_payment",
        help_text=_("Reference local payment transaction table"),
    )
    result = models.CharField(
        max_length=100, help_text=_("Status response from TAP gateway")
    )
    # payment details
    payment_url = models.CharField(
        max_length=250,
        help_text=_("Captures generated URL for user payment"),
        null=True,
    )
    charge_id = models.CharField(
        max_length=250,
        help_text=_("Charge ID returned from TAP"),
        unique=True,
        db_index=True,
    )
    init_response = models.JSONField(
        help_text=_("Response received when initiating the payment"),
        null=True,
        blank=True,
    )
    callback_response = models.JSONField(
        help_text=_("Callback response received after the payment is done"),
        null=True,
        blank=True,
    )
    # audit fields
    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True,
        help_text=_("Datetime when payment was initiated"),
    )
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True,)

    objects = TapPaymentManager()

    class Meta:
        verbose_name = _("TAP Payment")

    @property
    def amount(self):
        return self.payment.total_payment

    @property
    def currency(self):
        return self.callback_response["currency"] if self.callback_response else None

    def callback_update(self, tap_payload):
        apple_pay = getattr(settings, "APPLE_PAY", "apple_pay")
        google_pay = getattr(settings, "GOOGLE_PAY", "google_pay")
        if self.callback_response == None and self.source not in [
            apple_pay,
            google_pay,
        ]:
            self.result = tap_payload["status"]
            self.callback_response = tap_payload
            self.status = tap_payload["status"]
            self.save()
            self.mark_transaction(tap_payload["response"])
            logger.info(f"Mark TAP Transaction finished for charge ID {self.charge_id}")

    def mark_transaction(self, error_message=None):
        if self.status == self.Status.CAPTURED:
            self.payment.mark_paid()
        else:
            self.payment.mark_failed(error_message)


class TapCustomer(models.Model):
    customer = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tap_customer"
    )
    tap_customer_id = models.CharField(
        _("Tap customer id"), max_length=200, unique=True
    )
    first_name = models.CharField(_("First name"), max_length=200)
    last_name = models.CharField(_("Last name"), max_length=200)
    email = models.EmailField(_("Email"), unique=True, null=True)
    phone_number = PhoneNumberField(_("Phone number"), unique=True, null=True)
    init_data = models.JSONField()

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True,)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True,)

    def __str__(self) -> str:
        return f"{self.email} | {self.customer_id}"
