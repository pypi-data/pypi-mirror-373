from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from ob_dj_store.core.stores.managers import OrderItemManager, OrderManager
from ob_dj_store.utils.model import DjangoModelCleanMixin


class Order(DjangoModelCleanMixin, models.Model):
    """
    - Represent the order requested by a user
    - it contains order-items
    """

    class OrderType(models.TextChoices):
        PHYSICAL = "PHYSICAL", _("physical")
        GIFT = "GIFT", _("gift")
        WALLET = "WALLET", _("wallet")

    class OrderStatus(models.TextChoices):
        ACCEPTED = "ACCEPTED", _("accepted")
        CANCELLED = "CANCELLED", _("cancelled")
        PENDING = "PENDING", _("pending")
        PREPARING = "PREPARING", _("preparing")
        READY = "READY", _("ready for pickup")
        DELIVERED = "DELIVERED", _("delivered")
        PAID = "PAID", _("paid")
        OPENED = "OPENED", _("opened")
        DROPPED = "DROPPED", _("dropped")
        IN_DELIVERY = "IN_DELIVERY", _("in delivery")

    # Case of delivery
    # TODO: Probably we want to setup the on_delete to SET_NULL because orders is part of
    #       sales and even if a user deleted orders cannot disappear otherwise will reflect
    #       invalid sales figure; same can be applied for the store field
    discount = models.ForeignKey(
        "stores.Discount", on_delete=models.PROTECT, null=True, blank=True
    )
    customer = models.ForeignKey(
        get_user_model(), related_name="orders", on_delete=models.SET_NULL, null=True,
    )
    store = models.ForeignKey(
        "stores.Store",
        related_name="orders",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    shipping_method = models.ForeignKey(
        "stores.ShippingMethod",
        related_name="orders",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    payment_method = models.ForeignKey(
        "stores.PaymentMethod",
        related_name="orders",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    shipping_address = models.ForeignKey(
        "stores.address",
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True,
    )
    immutable_shipping_address = models.ForeignKey(
        "stores.ImmutableAddress",
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=32, default=OrderStatus.PENDING, choices=OrderStatus.choices,
    )
    # Add pickup time for an order, Pick up can be now or a later hour during the day
    pickup_time = models.DateTimeField(
        null=True, blank=True, help_text=_("Pickup time")
    )
    # Order id of the pickup_car
    car_id = models.PositiveIntegerField(null=True, blank=True)
    # Pick up can be now or a later hour during the day. If pickup_time is not set,
    extra_infos = models.JSONField(null=True, blank=True,)
    init_data = models.JSONField(null=True, blank=True)
    offer_redeemed = models.BooleanField(default=False)
    offer_id = models.IntegerField(null=True, blank=True, default=None)
    # TODO: add pick_up_time maybe ?
    # audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OrderManager()

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return f"Order(PK={self.pk})"

    # the order is scheduled for pickup
    @property
    def is_scheduled_for_pickup(self):
        return self.pickup_time is not None

    # the order is ready for pickup
    @property
    def is_ready_for_pickup(self):
        return self.status == Order.OrderStatus.READY

    # mark the order as ready for pickup

    def mark_as_ready_for_pickup(self):
        self.status = Order.OrderStatus.READY
        self.save()

    @property
    def get_discount_amount(self):
        return sum(map(lambda item: item.discount_offer_amount, self.items.all()))

    @property
    def total_amount(self):
        if self.type_of_order == Order.OrderType.WALLET.value:
            return Decimal(self.extra_infos["amount"])
        elif self.type_of_order == Order.OrderType.GIFT.value:
            return Decimal(self.extra_infos["gift_details"]["price"])
        amount = Decimal(
            sum(map(lambda item: Decimal(item.total_amount) or 0, self.items.all()))
        )
        if self.shipping_method:
            amount += self.shipping_method.shipping_fee
        amount -= self.get_discount_amount
        return amount

    @property
    def preparation_time(self):
        # Get the maximum preparation time among all items
        all_items = self.items.all()
        return max(item.preparation_time for item in all_items) if all_items else 0

    @property
    def type_of_order(self):
        if self.extra_infos:
            if self.extra_infos.get("gift_details", None):
                return self.OrderType.GIFT.value
            is_wallet = self.extra_infos.get("is_wallet_fill_up")
            if is_wallet:
                return self.OrderType.WALLET.value
        return self.OrderType.PHYSICAL.value

    def save(self, **kwargs):
        if not self.pk and self.shipping_address:
            self.immutable_shipping_address = self.shipping_address.to_immutable()
        return super().save(**kwargs)


class OrderItem(DjangoModelCleanMixin, models.Model):
    """OrderItem is detailed items of a given order, an order
    can contain one or more items purchased in the same transaction
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    # TODO: We should copy the product details to the item; because if a product is
    #       deleted then the OrderItem should maintain the product information
    product_variant = models.ForeignKey(
        "stores.ProductVariant",
        null=True,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    # notes for special instructions, can be empty
    notes = models.TextField(blank=True, null=True, help_text=_("Special instructions"))
    # attribute choices for the item
    attribute_choices = models.ManyToManyField(
        "stores.AttributeChoice",
        blank=True,
        related_name="order_items",
        help_text=_("Attribute choices for the item"),
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    quantity = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, message="Can you please provide a valid quantity !",)
        ],
        help_text=_("quantity of the variant"),
    )
    init_data = models.JSONField(null=True, blank=True)

    objects = OrderItemManager()

    def __str__(self):
        return f"OrderItem - {self.quantity} {self.product_variant.product.name}{self.product_variant.name}"

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")

    @property
    def attribute_choices_total_amount(self):
        total_price = Decimal(0)
        store = self.order.store
        if self.order.type_of_order == Order.OrderType.PHYSICAL.value and not store:
            raise ValidationError("Physical Order should have store object")
        for attribute_choice in self.attribute_choices.all():
            try:
                attribute_inventory = attribute_choice.attribute_inventory.get(
                    store=store
                )
            except ObjectDoesNotExist:
                raise ValidationError(
                    f"AttributeChoice(PK={attribute_choice.id}) does not have Inventory at Store(PK={store.id})"
                )
            total_price += attribute_inventory.price
        return total_price

    @property
    def discount_offer_amount(self):
        discount = self.order.discount
        if discount:
            return discount.perc_to_flat(self.total_amount)
        return Decimal(0)

    @property
    def total_amount(self):
        if self.total_price > 0:
            return self.total_price
        try:
            return (
                self.product_variant.inventories.get(store=self.order.store).price
                + self.attribute_choices_total_amount
            ) * self.quantity
        except ObjectDoesNotExist:
            return 0

    @property
    def preparation_time(self):
        try:
            return (
                self.product_variant.inventories.get(
                    store=self.order.store
                ).preparation_time.total_seconds()
                * self.quantity
            ) / 60
        except ObjectDoesNotExist:
            return 0

    @property
    def inventory(self):
        try:
            return self.product_variant.inventories.get(store=self.order.store)
        except ObjectDoesNotExist:
            return None


class OrderHistory(DjangoModelCleanMixin, models.Model):
    """
    - Represent the history of an order
    - it contains the status of the order
    """

    order = models.ForeignKey(Order, related_name="history", on_delete=models.CASCADE)
    status = models.CharField(max_length=32, choices=Order.OrderStatus.choices,)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Order History")
        verbose_name_plural = _("Order Histories")
        unique_together = (("order", "status"),)

    def __str__(self):
        return f"OrderHistory - {self.status}"
