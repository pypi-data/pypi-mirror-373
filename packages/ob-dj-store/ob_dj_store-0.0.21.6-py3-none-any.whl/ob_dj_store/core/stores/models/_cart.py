import logging
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from ob_dj_store.core.stores.managers import CartItemManager, CartManager
from ob_dj_store.core.stores.models._partner import PartnerAuthInfo
from ob_dj_store.core.stores.utils import round_up_tie

logger = logging.getLogger(__name__)


class Cart(models.Model):
    customer = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="cart",
        primary_key=True,
    )
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CartManager()

    class Meta:
        verbose_name_plural = _("Carts")
        verbose_name = _("Cart")

    @property
    def tax_amount(self) -> Decimal:
        amount = Decimal(
            sum(map(lambda item: Decimal(item.tax_amount), self.items.all()))
        )
        return round_up_tie(amount, 3)

    def get_applied_tax_amount(self):
        tax_amount = 0
        for item in self.items.all():
            tax = item.get_tax_object()
            if tax:
                if tax.is_applied:
                    tax_amount += item.tax_amount
        return Decimal(tax_amount)

    @property
    def total_price(self) -> Decimal:
        total_price = Decimal(0)
        for item in self.items.all():
            try:
                if item.inventory.quantity and item.inventory.quantity > 0:
                    total_price += item.total_price
            except AttributeError:
                logger.error(f"Item {item} has no inventory")
        return total_price

    @property
    def total_price_with_tax(self) -> Decimal:
        return self.total_price + self.get_applied_tax_amount()

    @property
    def full_price(self,) -> Decimal:
        return self.total_price_with_tax - self.discount_offer_amount

    @property
    def get_user_partner(self):
        try:
            partner_auth_info = PartnerAuthInfo.objects.get(
                user=self.customer,
                authentication_expires__gte=now(),
                partner__offer_start_time__lte=now(),
                partner__offer_end_time__gt=now(),
            )
            return partner_auth_info.partner
        except ObjectDoesNotExist:
            return None

    @property
    def discount_offer_amount(self):
        return round_up_tie(
            sum(map(lambda item: item.discount_amount, self.items.all())), 3
        )

    @property
    def total_price_with_discount(self):
        return self.total_price - Decimal(self.discount_offer_amount)

    def __str__(self):
        return f"Cart - {self.customer.email} with total price {self.total_price}"

    def fill(self, order):
        from ob_dj_store.core.stores.models._cart import CartItem

        order_items = order.items.all()
        for item in order_items:
            cart_item = CartItem.objects.create(
                cart=self,
                product_variant=item.product_variant,
                store=order.store,
                notes=item.notes,
                quantity=item.quantity,
            )
            attribute_choices = list(item.attribute_choices.all())
            if len(attribute_choices) > 0:
                cart_item.attribute_choices.set(attribute_choices)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product_variant = models.ForeignKey(
        "stores.ProductVariant", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    store = models.ForeignKey(
        "stores.Store",
        on_delete=models.CASCADE,
        related_name="store_items",
        null=True,
        blank=True,
    )
    # notes for special instructions, can be empty
    notes = models.TextField(blank=True, null=True, help_text=_("Special instructions"))
    notes_arabic = models.TextField(
        blank=True, null=True, help_text=_("Special instructions in arabic")
    )

    # attribute choices for the item
    attribute_choices = models.ManyToManyField(
        "stores.AttributeChoice",
        blank=True,
        related_name="cart_items",
        help_text=_("Attribute choices for the item"),
    )
    extra_infos = models.JSONField(null=True, blank=True)
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CartItemManager()

    class Meta:
        verbose_name_plural = _("Cart Items")
        verbose_name = _("Cart Item")
        ordering = [
            "created_at",
        ]

    @property
    def unit_price(self) -> Decimal:
        try:
            return self.product_variant.inventories.get(
                store=self.store
            ).discounted_price
        except ObjectDoesNotExist:
            return 0

    def get_tax_object(self):
        from ob_dj_store.core.stores.models import Tax

        if self.store:
            try:
                tax = Tax.objects.get(
                    country=self.store.address.country, is_active=True
                )
            except ObjectDoesNotExist:
                tax = None
        return tax

    @property
    def tax_amount(self) -> Decimal:
        from ob_dj_store.core.stores.models import Tax

        tax = self.get_tax_object()
        if tax:
            if tax.rate == Tax.Rates.PERCENTAGE:
                value = Decimal(
                    (self.total_price - self.discount_amount) * tax.value / 100
                )
                return value
            return tax.value
        return 0

    @property
    def discount_amount(self):
        partner = self.cart.get_user_partner
        if partner:
            if partner.discount and partner.stores.filter(pk=self.store.pk).exists():
                return partner.discount.perc_to_flat(self.total_price)
        return Decimal(0)

    @property
    def attribute_choices_total_price(self) -> Decimal:
        total_price = Decimal(0)
        if not self.store:
            raise ValidationError("Cart items should have store object")
        for attribute_choice in self.attribute_choices.all():
            try:
                attribute_inventory = attribute_choice.attribute_inventory.get(
                    store=self.store
                )
            except ObjectDoesNotExist:
                raise ValidationError(
                    f"AttributeChoice(PK={attribute_choice.id}) does not have Inventory at Store(PK={self.store.id})"
                )
            total_price += attribute_inventory.price
        return total_price

    @property
    def inventory(self) -> Decimal:
        try:
            return self.product_variant.inventories.get(store=self.store)
        except ObjectDoesNotExist:
            return None

    def clean(self):
        super(CartItem, self).clean()
        if self.product_variant.product.type == "PHYSICAL" and not self.store:
            raise ValidationError(_("The store attribute can not be null"))

    @property
    def total_price(self) -> Decimal:
        return (self.unit_price + self.attribute_choices_total_price) * self.quantity

    def __str__(self):
        return f"CartItem - {self.quantity} {self.product_variant.name}"
