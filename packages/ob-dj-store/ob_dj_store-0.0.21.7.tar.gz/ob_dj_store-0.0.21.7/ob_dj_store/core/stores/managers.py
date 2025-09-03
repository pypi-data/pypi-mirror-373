import json
import logging
import typing
from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from config import settings
from ob_dj_store.utils.helpers import import_gift_payment_function

logger = logging.getLogger(__name__)


class ActiveMixin:
    def active(self):
        return self.filter(is_active=True)


class StoreManager(ActiveMixin, models.Manager):
    pass


class CategoryManager(ActiveMixin, models.Manager):
    pass


class ProductVariantManager(models.Manager):
    def active(self):
        pass


class ProductManager(ActiveMixin, models.Manager):
    pass


class CartManager(models.Manager):
    pass


class CartItemManager(models.Manager):
    pass


class ShippingMethodManager(ActiveMixin, models.Manager):
    pass


class PaymentMethodManager(ActiveMixin, models.Manager):
    pass


class PaymentManager(models.Manager):
    def create(self, currency: str, *args: typing.Any, **kwargs: typing.Any):
        from ob_dj_store.core.stores.gateway.stripe.models import StripePayment
        from ob_dj_store.core.stores.gateway.tap.models import TapPayment
        from ob_dj_store.core.stores.models import Tax, WalletTransaction

        orders = kwargs.pop("orders", None)
        if not orders:
            raise ValidationError(
                {"order", _("You cannot perform payment without items")}
            )
        try:
            if orders[0].store and orders[0].type_of_order == "PHYSICAL":
                kwargs["payment_tax"] = Tax.objects.get(
                    country=orders[0].store.address.country, is_active=True
                )
        except ObjectDoesNotExist:
            raise ValidationError({"tax": _("Tax object is missing")})
        gateway = settings.DEFAULT_PAYMENT_METHOD
        method = kwargs.get("method", None)
        if method:
            gateway = method.payment_provider
        instance: "models.Payment" = super().create(currency=currency, *args, **kwargs)
        instance.orders.set(orders)
        if gateway in [
            settings.TAP_CREDIT_CARD,
            settings.TAP_KNET,
            settings.TAP_ALL,
            settings.APPLE_PAY,
            settings.GOOGLE_PAY,
            settings.MADA,
            settings.BENEFIT,
        ]:
            source = gateway
            TapPayment.objects.create(
                source=source, payment=instance, user=kwargs.get("user"),
            )
            return instance
        elif gateway == settings.STRIPE:
            StripePayment.objects.create(
                payment=instance, user=kwargs.get("user"),
            )
            return instance
        elif gateway == settings.WALLET:
            try:
                wallet = kwargs["user"].wallets.get(currency=currency)
            except ObjectDoesNotExist:
                instance.mark_failed("Wallet Not Found")
                raise ValidationError({"wallet": _("Wallet Not Found")})
            WalletTransaction.objects.create(
                wallet=wallet,
                type=WalletTransaction.TYPE.DEBIT,
                amount=kwargs["amount"],
            )
        elif gateway == settings.GIFT:
            gift_payment_path = getattr(settings, "GIFT_PAYMENT_METHOD_PATH", None)
            payment_funciton = import_gift_payment_function(gift_payment_path)
            response = payment_funciton(
                gift_card_id=orders[0].extra_infos["gift_card"], payment=instance
            )
            if not response["success"]:
                instance.mark_failed(response["error"])
                raise ValidationError({"gift_card": response["error"]})
        instance.mark_paid()
        return instance


class InventoryManager(ActiveMixin, models.Manager):
    pass


class OrderItemManager(models.Manager):
    def create(self, attributes=[], *args, **kwargs):
        order_item = super().create(**kwargs)
        order_item.attribute_choices.set(attributes)
        inventory_price = (
            round(float(order_item.inventory.price), 3) if order_item.inventory else 0
        )
        store = order_item.order.store
        attribute_choices_price = sum(
            map(lambda item: float(item.get_price(store)) or 0, attributes)
        )
        total_price = round(
            (inventory_price + attribute_choices_price) * int(order_item.quantity), 3
        )
        init_data = {
            "inventory_price": inventory_price,
            "product_variant": f"{order_item.product_variant.product.name} {order_item.product_variant.name}",
            "quantity": order_item.quantity,
            "attribute_choices": [
                {
                    "name": attribute.name,
                    "price": round(float(attribute.get_price(store)), 3),
                }
                for attribute in attributes
            ],
            "total_price": total_price,
        }
        order_item.total_price = Decimal(total_price).quantize(Decimal("0.000"))
        order_item.init_data = json.dumps(init_data)
        order_item.save()
        return order_item


class OrderManager(models.Manager):
    def create(self, *args, **kwargs):
        from ob_dj_store.apis.stores.rest.serializers.serializers import (
            OrderDataSerializer,
        )
        from ob_dj_store.core.stores.models._partner import PartnerAuthInfo

        try:
            partner_auth_info = PartnerAuthInfo.objects.get(
                user=kwargs["customer"],
                authentication_expires__gte=now(),
                partner__offer_start_time__lte=now(),
                partner__offer_end_time__gt=now(),
            )
        except ObjectDoesNotExist:
            partner_auth_info = None
        if partner_auth_info:
            partner = partner_auth_info.partner
            store = kwargs.get("store", None)
            if store:
                if partner.stores.filter(pk=kwargs["store"].pk).exists():
                    kwargs["discount"] = partner.discount
        order = super().create(**kwargs)
        serializer = OrderDataSerializer(order)
        order.init_data = serializer.data
        order.save()
        return order


class FavoriteManager(ActiveMixin, models.Manager):
    def favorites_for_user(self, user):
        """Returns Favorites for a specific user"""
        return self.get_queryset().filter(user=user)

    def favorites_for_model(self, model, user=None):
        """Returns Favorites for a specific model"""
        content_type = ContentType.objects.get_for_model(model)
        qs = self.get_queryset().filter(content_type=content_type).only("id")
        if user:
            qs = qs.filter(user=user)
        return qs

    def favorites_for_object(self, obj, user=None):
        """Returns Favorites for a specific object"""
        content_type = ContentType.objects.get_for_model(type(obj))
        qs = self.get_queryset().filter(content_type=content_type, object_id=obj.pk)
        if user:
            qs = qs.filter(user=user)

        return qs

    def favorite_for_user(self, obj, user):
        """Returns the favorite, if exists for obj by user"""
        content_type = ContentType.objects.get_for_model(type(obj))
        return self.get_queryset().get(content_type=content_type, object_id=obj.pk)


class FavoriteExtraManager(ActiveMixin, models.Manager):
    def extras_for_favorite(self, favorite):
        """Returns extras for a specific favorite"""
        return self.get_queryset().filter(favorite=favorite)


class InventoryOperationsManager(ActiveMixin, models.Manager):

    # override create method to set the inventory_quantity
    def create(self, *args, **kwargs):
        from ob_dj_store.core.stores.models._inventory import (
            Inventory,
            InventoryOperations,
        )

        # based on the operation type, set the inventory_quantity
        # get the store and the product variant in the kwargs
        store = kwargs.get("store")
        product_variant = kwargs.get("product_variant")
        # get the inventory_quantity from the product variant
        if inventory := Inventory.objects.filter(
            store=store, variant=product_variant
        ).first():
            inventory_quantity = inventory.quantity
            operation_quantity = kwargs.get("quantity")

            if (
                kwargs.get("type_of_operation")
                == InventoryOperations.Type_of_operation.STOCK_IN
            ):
                inventory_quantity += operation_quantity
            elif (
                kwargs.get("type_of_operation")
                == InventoryOperations.Type_of_operation.STOCK_OUT
            ):
                inventory_quantity -= operation_quantity

            inventory.quantity = inventory_quantity
            inventory.save()

        return super().create(*args, **kwargs)


class FeedbackAttributeManager(models.Manager):
    def create(self, **kwargs):
        if "attribute" in kwargs:
            config = self.model.config.field.related_model.objects.get(
                attribute=kwargs["attribute"]
            )
            del kwargs["attribute"]
            kwargs["config"] = config
        return super().create(**kwargs)


class ProductVariantStoreManager(models.Manager):
    def create(self, *args, **kwargs):
        return super().create(*args, **kwargs)


class WalletTransactionManager(models.Manager):
    def create(self, *args, **kwargs):
        from ob_dj_store.core.stores.models._wallet import WalletTransaction

        wallet = kwargs["wallet"]
        type = kwargs["type"]
        if type == WalletTransaction.TYPE.DEBIT and wallet.balance < kwargs["amount"]:
            raise ValidationError(_("Insufficient Funds"))
        return super().create(*args, **kwargs)


class PartnerAuthInfoManager(models.Manager):
    def create(self, *args, **kwargs):
        return super().create(*args, **kwargs)


class CountryPaymentMethodManager(ActiveMixin, models.Manager):
    pass
