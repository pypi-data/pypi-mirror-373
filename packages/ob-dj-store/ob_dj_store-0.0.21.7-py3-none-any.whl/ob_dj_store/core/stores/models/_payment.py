import logging
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from config import settings as store_settings
from ob_dj_store.core.stores.managers import PaymentManager
from ob_dj_store.core.stores.models import Order

logger = logging.getLogger(__name__)


class Tax(models.Model):
    """
    As a user, I should be able to see tax added to my payment summary of each order.
    Tax should be a model holding "name", "country" ,"description" and "rate".
    Rate should be one of two types, either percentage or flat, and it should have a value.
    Tax should be calculated with the order total once the order moves to payment process
    """

    class Rates(models.TextChoices):
        PERCENTAGE = "PERCENTAGE", _("percentage")
        FLAT = "FLAT", _("flat")

    description = models.TextField(null=True, blank=True)
    name = models.CharField(max_length=200, help_text=_("Name"))
    rate = models.CharField(
        max_length=32, choices=Rates.choices, help_text="Tax Rate for the given payment"
    )
    is_applied = models.BooleanField(default=True)
    country = CountryField(help_text=_("The address country."), default="KW")
    value = models.DecimalField(
        blank=True,
        max_digits=5,
        decimal_places=3,
        null=True,
        help_text="Value for the given Payment -> 0.0625",
    )
    is_active = models.BooleanField(default=False)
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("country",)

    @property
    def value_to_percentage(self) -> Decimal:
        """Converts tax value to percentage
        Args:
            value (Decimal): Value
        Returns:
            Decimal: Tax Value Percentage Example -> 6.2500
        """
        return "{:.2%}".format(self.value)


class Payment(models.Model):
    """Payment captures the order payment either COD or via a Gateway"""

    class PaymentStatus(models.TextChoices):
        INIT = "INIT"
        SUCCESS = "SUCCESS"
        FAILED = "FAILED"
        ERROR = "ERROR"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="user_payments",
    )
    status = models.CharField(
        max_length=100, default=PaymentStatus.INIT, choices=PaymentStatus.choices,
    )
    method = models.ForeignKey(
        "stores.PaymentMethod", on_delete=models.CASCADE, null=True, blank=True,
    )
    payment_tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True,)
    orders = models.ManyToManyField("stores.Order", related_name="payments")
    amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
    )
    currency = models.CharField(_("Currency"), max_length=10)
    result = models.TextField(null=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    payment_post_at = models.DateTimeField(_("Payment Post At"), null=True, blank=True)

    objects = PaymentManager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment (PK={self.pk})"

    def mark_paid(self):
        """
        mark payment and orders as paid then perform post payment actions
        if wallet fill up we add wallet transaction to the user
        if physical order we decrease the quantity from inventory and delete items from cart
        """
        from ob_dj_store.core.stores.models._wallet import WalletTransaction

        self.status = self.PaymentStatus.SUCCESS
        orders = self.orders.all()
        if orders[0].type_of_order == Order.OrderType.WALLET.value:
            order = orders[0]
            currency = order.extra_infos["currency"]
            wallet = self.user.wallets.get(currency=currency)
            WalletTransaction.objects.create(
                wallet=wallet,
                amount=self.amount,  # TODO: cunfused about how we hundle if he want to fill up other currency
                type=WalletTransaction.TYPE.CREDIT,
            )
            order.status = Order.OrderStatus.PAID
            order.save()
        else:
            cart = self.user.cart
            for order in orders:
                order.status = Order.OrderStatus.PAID
                for item in order.items.all():
                    if item.inventory:
                        item.inventory.decrease(item.quantity)
                order.save()
                items = order.store.store_items.filter(cart=cart)
                items.delete()
        self.payment_post_at = timezone.now()
        self.save()

    def mark_failed(self, message):
        self.status = self.PaymentStatus.FAILED
        self.result = message
        orders = self.orders.all()
        for order in orders:
            order.status = Order.OrderStatus.CANCELLED
            order.save()
        self.save()

    @property
    def total_payment(self):
        orders = self.orders.all()
        sum_orders = Decimal(
            sum(map(lambda order: Decimal(order.total_amount) or 0, orders))
        )
        if not self.payment_tax:
            return sum_orders
        elif not self.payment_tax.is_applied:
            return sum_orders
        elif self.payment_tax.rate == Tax.Rates.PERCENTAGE:
            perc = Decimal(sum_orders * self.payment_tax.value / 100)
            return round(sum_orders + perc, 3)

        return round(sum_orders + self.payment_tax.value, 3)

    @property
    def type_of_order(self):
        order = self.orders.all().first()
        if order:
            return order.type_of_order
        return None

    @property
    def payment_url(self):
        payment_url = None
        gateway = store_settings.DEFAULT_PAYMENT_METHOD
        if self.method:
            gateway = self.method.payment_provider
        if gateway in [
            settings.TAP_CREDIT_CARD,
            settings.TAP_KNET,
            settings.TAP_ALL,
            settings.MADA,
            settings.BENEFIT,
        ]:
            payment_url = self.tap_payment.payment_url
        elif gateway == settings.STRIPE:
            # For Stripe, return the client_secret which is used by Stripe.js
            if hasattr(self, "stripe_payment"):
                payment_url = self.stripe_payment.payment_url
        return payment_url
