import logging
import typing
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _

from ob_dj_store.core.stores.managers import WalletTransactionManager
from ob_dj_store.core.stores.models._store import PaymentMethod
from ob_dj_store.core.stores.utils import validate_currency
from ob_dj_store.utils.helpers import wallet_media_upload_to
from ob_dj_store.utils.model import DjangoModelCleanMixin

logger = logging.getLogger(__name__)


class WalletMedia(DjangoModelCleanMixin, models.Model):
    """
    selection images for wallets.
    """

    image = models.ImageField(upload_to=wallet_media_upload_to)
    image_thumbnail_medium = models.ImageField(
        upload_to="wallets/", null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"WalletMedia(PK={self.pk})"

    def save(self, *args, **kwargs):
        # If the current instance is set as primary, unset any existing primary images for the product
        if self.is_default:
            WalletMedia.objects.filter(is_default=True).update(is_default=False)
        elif not WalletMedia.objects.filter(is_default=True).exists():
            # If there are no primary images for the product, set the current instance as primary
            self.is_default = True
        super(WalletMedia, self).save(*args, **kwargs)


class Wallet(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallets",
    )
    name = models.CharField(max_length=200, null=True, blank=True)
    name_arabic = models.CharField(max_length=200, null=True, blank=True)
    media_image = models.ForeignKey(
        WalletMedia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wallets",
    )
    currency = models.CharField(
        max_length=3, default="KWD", validators=[validate_currency,],
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("user", "currency")

    def __str__(self) -> typing.Text:
        return f"{self.user.email} | {self.currency}"

    @property
    def balance(self) -> Decimal:
        from ob_dj_store.core.stores.models import WalletTransaction

        query = self.transactions.aggregate(
            balance=Coalesce(
                models.Sum(
                    "amount", filter=models.Q(type=WalletTransaction.TYPE.CREDIT),
                ),
                models.Value(Decimal(0)),
                output_field=models.DecimalField(),
            )
            - Coalesce(
                models.Sum(
                    "amount", filter=models.Q(type=WalletTransaction.TYPE.DEBIT)
                ),
                models.Value(Decimal(0)),
                output_field=models.DecimalField(),
            )
        )
        return query["balance"]

    @property
    def image_url(self):
        if self.media_image:
            image = self.media_image.image_thumbnail_medium
            return image.url if image else None

    def top_up_wallet(
        self, amount: Decimal, payment_method: PaymentMethod, extra_infos: dict = {}
    ):
        from ob_dj_store.core.stores.models import Order, Payment

        extra_infos.update(
            {
                "is_wallet_fill_up": True,
                "amount": str(amount),
                "currency": self.currency,
            }
        )
        user = self.user
        order = Order.objects.create(
            customer=user, payment_method=payment_method, extra_infos=extra_infos,
        )
        payment = Payment.objects.create(
            orders=[order,],
            user=user,
            currency=self.currency,
            method=payment_method,
            amount=amount,
        )
        tap_payment = payment.tap_payment
        return (tap_payment.payment_url, tap_payment.charge_id)


class WalletTransaction(models.Model):
    """

    As a user, I should be able to view my wallet transactions (debit/credit).
    WalletTransaction type should be one of two types, either debit or credit.

    """

    class TYPE(models.TextChoices):
        CREDIT = "CREDIT", _("credit")
        DEBIT = "DEBIT", _("debit")

    class CashBackType(models.TextChoices):
        BY_ORDER = "BY_ORDER", _("By Order")
        BY_OFFER = "BY_OFFER", _("By Offer")
        BY_STREAK = "BY_STREAK", _("By Streak")

    wallet = models.ForeignKey(
        "stores.Wallet", on_delete=models.CASCADE, related_name="transactions",
    )
    type = models.CharField(max_length=100, choices=TYPE.choices,)

    amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
    )

    is_by_admin = models.BooleanField(default=False)
    is_cashback = models.BooleanField(default=False)
    is_refund = models.BooleanField(default=False)
    is_redeemed = models.BooleanField(default=False)
    cashback_type = models.CharField(
        max_length=100, choices=CashBackType.choices, blank=True, null=True
    )
    objects = WalletTransactionManager()

    # Audit
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    def __str__(self):
        return f"WalletTransaction (PK={self.pk})"
