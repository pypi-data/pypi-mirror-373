import calendar
import logging
import typing
from collections import OrderedDict
from datetime import datetime, timedelta
from decimal import Decimal

import pycountry
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import validate_email
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.module_loading import import_string
from django.utils.timezone import localtime, now
from django.utils.translation import gettext_lazy as _
from ob_dj_otp.core.otp.models import OneTruePairing
from phonenumber_field.phonenumber import to_python
from rest_framework import serializers

from config import settings as store_settings
from ob_dj_store.core.stores.models import (
    Attribute,
    AttributeChoice,
    Cart,
    CartItem,
    Category,
    CountryPaymentMethod,
    Discount,
    Favorite,
    FavoriteExtra,
    Feedback,
    FeedbackAttribute,
    FeedbackConfig,
    OpeningHours,
    Order,
    OrderHistory,
    OrderItem,
    Partner,
    PartnerAuthInfo,
    PartnerOTPAuth,
    Payment,
    PaymentMethod,
    PhoneContact,
    Product,
    ProductAttribute,
    ProductMedia,
    ProductTag,
    ProductVariant,
    ShippingMethod,
    Store,
    Tax,
    Wallet,
    WalletMedia,
    WalletTransaction,
)
from ob_dj_store.core.stores.models._inventory import Inventory
from ob_dj_store.core.stores.utils import PartnerAuth, distance, get_currency_by_country

logger = logging.getLogger(__name__)

from rest_framework import serializers


class ArabicFieldsMixin:
    """
    Serializer mixin to include or exclude Arabic fields based on the request header.
    """

    ARABIC_LANGUAGE_CODE = "AR"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arabic_field_suffixes = [
            "_arabic",
            "arabic_",
        ]  # Add other suffixes as needed

    def should_include_arabic_fields(self, request):
        """
        Check if the request header includes the Arabic language.
        """
        language_header = request.META.get("HTTP_LANGUAGE", "").upper()
        return language_header == self.ARABIC_LANGUAGE_CODE

    def to_representation(self, instance):
        request = self.context.get("request")
        data = super().to_representation(instance)
        if request and self.should_include_arabic_fields(request):
            data_output = {}
            for field_name, field_instance in data.items():
                for suffix in self.arabic_field_suffixes:
                    if field_name.endswith(suffix) or field_name.startswith(suffix):
                        original_field_name = field_name.replace(suffix, "")
                        data_output[original_field_name] = (
                            field_instance
                            if field_instance
                            else data[original_field_name]
                        )
            data.update(data_output)
        return data


class AttributeChoiceSerializer(ArabicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = AttributeChoice
        fields = (
            "id",
            "name",
            "name_arabic",
            "label",
            "label_arabic",
            "is_default",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        store = self.context.get("store", None)
        if not store and self.context.get("view", None):
            store = self.context["view"].kwargs.get("store_pk", None)
        if store:
            try:
                attribute_inventory = instance.attribute_inventory.get(store=store)
                data["price"] = attribute_inventory.price
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    f"AttributeChoice(PK={instance.pk}) doesnt have inventory at Store(PK={store})"
                )

        return data


class AttributeSerializer(ArabicFieldsMixin, serializers.ModelSerializer):
    attribute_choices = AttributeChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Attribute
        fields = (
            "id",
            "name",
            "name_arabic",
            "attribute_choices",
        )


class InventoryValidationMixin:
    def validate(self, attrs: typing.Dict) -> typing.Dict:
        validated_data = super().validate(attrs)
        inventory = None
        try:
            inventory = validated_data["product_variant"].inventories.get(
                store=validated_data["store"]
            )
        except:
            raise serializers.ValidationError(_("Product has no inventory"))
        if validated_data["quantity"] < 1:
            raise serializers.ValidationError(_("Quantity must be greater than 0."))
        # validate quantity in inventory
        if not inventory.is_uncountable:
            stock_quantity = inventory.quantity
            if validated_data["quantity"] > stock_quantity:
                raise serializers.ValidationError(
                    _("Quantity is greater than the stock quantity.")
                )
        return validated_data


class OpeningHourSerializer(ArabicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = OpeningHours
        fields = "__all__"


class ShippingMethodSerializer(ArabicFieldsMixin, serializers.ModelSerializer):
    name_extra = serializers.SerializerMethodField("get_name_extra")

    class Meta:
        model = ShippingMethod
        fields = (
            "id",
            "type",
            "shipping_fee_option",
            "name",
            "name_arabic",
            "description",
            "description_arabic",
            "is_active",
            "shipping_fee",
            "order_value",
            "name_extra",
        )

    def get_name_extra(self, obj):
        return obj.name


class OrderHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderHistory
        fields = (
            "id",
            "order",
            "status",
            "created_at",
        )


class OrderItemSerializer(InventoryValidationMixin, serializers.ModelSerializer):
    store = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product_variant",
            "quantity",
            "store",
            "total_amount",
            "preparation_time",
            "notes",
            "attribute_choices",
            "attribute_choices_total_amount",
        )

    def create(self, validated_data):
        validated_data.pop("store")
        return super().create(**validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not instance.order.store:
            raise serializers.ValidationError(
                f"Physical Order(PK={instance.order.pk}) doesnt not have store object"
            )
        self.context["store"] = instance.order.store
        representation["attribute_choices"] = AttributeChoiceSerializer(
            instance.attribute_choices.all(), many=True, context=self.context
        ).data

        return representation


class DiscountSerializer(serializers.ModelSerializer):
    discount_rate_perc = serializers.SerializerMethodField()

    class Meta:
        model = Discount
        fields = ("id", "discount_rate", "is_active", "discount_rate_perc")

    def get_discount_rate_perc(self, obj):
        return obj.discount_rate * 100


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    history = OrderHistorySerializer(many=True, read_only=True)
    estimated_timeline = serializers.SerializerMethodField()
    store_name = serializers.SerializerMethodField()
    discount = DiscountSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "store",
            "discount",
            "shipping_method",
            "payment_method",
            "shipping_address",
            "customer",
            "type_of_order",
            "status",
            "items",
            "total_amount",
            "preparation_time",
            "estimated_timeline",
            "get_discount_amount",
            "history",
            "car_id",
            "pickup_time",
            "extra_infos",
            "created_at",
            "updated_at",
            "store_name",
        )
        extra_kwargs = {
            "customer": {"read_only": True},
            "store": {"read_only": True, "required": False},
            "type_of_order": {"read_only": True, "required": False},
        }

    def get_estimated_timeline(self, obj):
        timeline = {
            "pending": obj.created_at,
            "received": None,
            "order_ready": None,
            "delivering": None,
            "ready": None,
        }
        payment = obj.payments.all().first()
        if not payment:
            return timeline
        if payment.payment_post_at:
            timeline["received"] = payment.payment_post_at
            timeline["order_ready"] = payment.payment_post_at + timedelta(
                minutes=obj.preparation_time
            )
            if not obj.is_scheduled_for_pickup and obj.shipping_method:
                timeline["delivering"] = timeline["order_ready"] + timedelta(
                    minutes=store_settings.ESTIMATED_DELIVERING_TIME
                )
            timeline["ready"] = timeline["delivering"] or timeline["order_ready"]
        return timeline

    def get_store_name(self, obj):
        return obj.store.name if obj.store else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

    def _get_store(self):
        store_pk = self.context["view"].kwargs["store_pk"]
        try:
            store = Store.objects.get(pk=store_pk)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(_("Store does not exist!"))
        return store

    def _validate_user_address(
        self, attrs,
    ):
        if "shipping_address" not in attrs:
            raise ValidationError(
                {"shipping_address": _("Please provide a delivery address.")}
            )
        shipping_address = attrs["shipping_address"]
        store = attrs["store"]
        if store.poly:
            if not store.poly.contains(shipping_address.location):
                raise ValidationError(
                    {
                        "shipping_address": _(
                            "The shipping address you provided is outside of the store's delivery range."
                        )
                    }
                )
        else:
            logger.error(f"Store {store.name} support delivery but doesn't have a poly")
            raise ValidationError(
                {"store": _("Delivery is not supported by this store.")}
            )

    def _validate_digital_product(self, gift_details, attrs):
        errors = []
        for key in settings.DIGITAL_PRODUCTS_REQUIRED_KEYS:
            if not (key in gift_details.keys() and len(str(gift_details.get(key)))):
                errors.append({key: "This field should be filled."})
        if len(errors) > 0:
            raise serializers.ValidationError(errors)
        email = gift_details.get("email")
        phone_number = gift_details.get("phone_number")
        user = self.context["request"].user
        if email and phone_number:
            raise serializers.ValidationError(
                _("Both Email and Phone number cannot be provided.")
            )
        elif not email and not phone_number:
            raise serializers.ValidationError(_("Email or Phone number is required."))
        elif phone_number and not to_python(phone_number).is_valid():
            raise serializers.ValidationError(_("Invalid Phone number format."))
        elif email:
            try:
                validate_email(email)
            except ValidationError:
                raise serializers.ValidationError(_("Invalid Email format."))
        try:
            if not gift_details["currency"]:
                gift_details["currency"] = get_currency_by_country(user.country.code)

        except Exception:
            raise serializers.ValidationError("Currency is required")
        if not pycountry.currencies.get(alpha_3=gift_details["currency"]):
            raise serializers.ValidationError("Gift currency is not valid")
        try:
            product = Product.objects.get(id=gift_details["digital_product"])
        except ObjectDoesNotExist:
            raise serializers.ValidationError(_("Digital product does not exist!"))
        if product.type == Product.ProductTypes.PHYSICAL:
            raise serializers.ValidationError(
                _("You must not fill extra infos for physical products.")
            )

        gift_minimun_amount = store_settings.GIFT_MINIMUM_AMOUNT.get(
            attrs["store"].currency, 5
        )
        if gift_details["price"] <= gift_minimun_amount - 1:
            raise serializers.ValidationError(_("Gift card amount is not valid!"))

    def _validate_pickup_time(self, store, pickup_time):
        # validate that the pickup_time is always in the future

        if pickup_time < localtime(now()):
            raise serializers.ValidationError(_("Pickup time must be in the future"))
        pickup_time_time = pickup_time.time()
        # validate that the pickup_time is between store's opening hours and closing hours
        try:
            op_hour = store.opening_hours.get(weekday=pickup_time.weekday() + 1)
            from_hour = op_hour.from_hour
            to_hour = op_hour.to_hour
            if store.currency == "AED":
                try:
                    pickup_time_time += timedelta(hours=1)
                except Exception as e:
                    logger.info(
                        f"The fix for UAE stores timezone failed due to this error {e}"
                    )

            if (
                op_hour.is_open_after_midnight
                and not op_hour.always_open
                and (pickup_time_time > to_hour and pickup_time_time < from_hour)
            ):
                raise serializers.ValidationError(
                    _("Pickup time must be between store's opening hours")
                )
            if (
                not op_hour.is_open_after_midnight
                and not op_hour.always_open
                and not from_hour <= pickup_time_time <= to_hour
            ):
                raise serializers.ValidationError(
                    _("Pickup time must be between store's opening hours")
                )

        except ObjectDoesNotExist:
            logger.error(f"{store.name} Store doesn't have opening hours for ")

    def validate(self, attrs):
        language = (
            True
            if self.context["request"].META.get("HTTP_LANGUAGE", "") == "AR"
            else False
        )
        user = self.context["request"].user
        attrs["store"] = self._get_store()
        if not "extra_infos" in attrs:
            attrs["extra_infos"] = {}
        stores = Store.objects.filter(store_items__cart=user.cart).distinct()
        gift_details = attrs["extra_infos"].get("gift_details", None)
        unavailable_items = []
        if gift_details:
            self._validate_digital_product(gift_details, attrs)
            currency = gift_details["currency"]
        # The Cart items must not be empty
        elif not user.cart.items.exists():
            raise serializers.ValidationError(_("The Cart must not be empty"))
        else:
            if not store_settings.DIFFERENT_STORE_ORDERING:
                if len(stores) > 1:
                    raise ValidationError(_("You cannot order from different stores"))
                for item in user.cart.items.all():
                    if item.inventory:
                        if item.inventory.is_snoozed:
                            unavailable_items.append(item)
                        elif not item.inventory.is_uncountable:
                            if (
                                not item.inventory.quantity
                                or item.inventory.quantity == 0
                            ):
                                unavailable_items.append(item)

                    elif not item.inventory:
                        if language and item.product_variant.product.name_arabic:
                            product_name = item.product_variant.product.name_arabic
                        else:
                            product_name = item.product_variant.product.name

                        variant_name = item.product_variant.name
                        message = (
                            f"{product_name} {variant_name} doesn't exist on this store"
                        )
                        unavailable_items.append(item)
                        raise ValidationError(_(message))
                if unavailable_items:
                    raise ValidationError(
                        _(
                            "The cart has items that are not available in the selected store"
                        )
                    )
            if "shipping_method" in attrs:
                if (
                    attrs["shipping_method"].type
                    == ShippingMethod.ShippingType.DELIVERY
                ):
                    self._validate_user_address(attrs)
            currency = attrs["store"].currency

        if attrs.get("pickup_time", None):
            self._validate_pickup_time(attrs["store"], attrs["pickup_time"])

        payment_method = attrs.get("payment_method")
        if payment_method:
            if payment_method.payment_provider == store_settings.WALLET:
                try:
                    wallet = user.wallets.get(currency=currency)
                except ObjectDoesNotExist:
                    raise serializers.ValidationError(
                        {"wallet": _(f"{currency} is not a valid currency")}
                    )

                if gift_details:
                    amount = gift_details["price"]
                else:
                    amount = user.cart.full_price

                if wallet.balance < amount:
                    raise serializers.ValidationError(
                        {"wallet": _("Insufficient Funds")},
                    )
            elif payment_method.payment_provider == store_settings.GIFT:
                if not attrs["extra_infos"].get("gift_card", None):
                    raise serializers.ValidationError(
                        {"gift": _("The Gift card is missing")}
                    )

        return super().validate(attrs)

    def perform_payment(self, amount, payment_method, order_store, orders, currency):
        from django.conf import settings

        from ob_dj_store.core.stores.gateway.stripe.utils import StripeException
        from ob_dj_store.core.stores.gateway.tap.utils import TapException

        user = self.context["request"].user
        payment_transaction = None
        charge_id = None

        try:
            payment = Payment.objects.create(
                user=user,
                amount=amount,
                method=payment_method,
                currency=currency,
                orders=orders,
            )

            # Handle different payment gateways
            if payment_method and payment_method.payment_provider == settings.STRIPE:
                payment_transaction = payment.stripe_payment
                charge_id = (
                    payment_transaction.payment_intent_id
                    if payment_transaction
                    else None
                )
            elif payment_method and payment_method.payment_provider in [
                settings.TAP_CREDIT_CARD,
                settings.TAP_KNET,
                settings.TAP_ALL,
                settings.MADA,
                settings.BENEFIT,
            ]:
                payment_transaction = payment.tap_payment
                charge_id = (
                    payment_transaction.charge_id if payment_transaction else None
                )

        except ValidationError as err:
            raise serializers.ValidationError(detail=err.messages)
        except (TapException, StripeException) as err:
            raise serializers.ValidationError({"payment_gateway": _(str(err))})
        except ObjectDoesNotExist as err:
            logger.info(
                f"Payment Object not created: user:{user}, method:{payment_method}, currency:{currency}, error:{err}"
            )

        return {
            "orders": orders,
            "payment_url": payment.payment_url,
            "charge_id": charge_id,
        }

    def create(self, validated_data: typing.Dict):
        user = self.context["request"].user
        orders = []
        order_store = validated_data["store"]
        gift_details = validated_data["extra_infos"].get("gift_details", None)
        if gift_details:
            amount = gift_details["price"]
            order = Order.objects.create(customer=user, **validated_data)
            orders.append(order)
            try:
                default_currency = get_currency_by_country(user.country.code)
            except Exception as e:
                default_currency = "KWD"
                logger.info(f"Couldn't fetch currency due to this error {e}")
            currency = gift_details.get("currency", default_currency)
        else:
            cart = user.cart
            stores = Store.objects.filter(store_items__cart=cart).distinct()
            orders = []
            validated_data.pop("store")
            for store in stores:
                order = Order.objects.create(
                    store=store, customer=cart.customer, **validated_data
                )
                items = store.store_items.filter(cart=cart)
                for item in items:
                    order_item = OrderItem.objects.create(
                        order=order,
                        product_variant=item.product_variant,
                        quantity=item.quantity,
                        attributes=list(item.attribute_choices.all()),
                        notes=item.notes,
                    )
                orders.append(order)
            amount = Decimal(
                sum(map(lambda order: Decimal(order.total_amount) or 0, orders))
            )
            currency = order_store.currency

        payment_method = validated_data.get("payment_method")
        return self.perform_payment(
            amount=amount,
            payment_method=payment_method,
            order_store=order_store,
            orders=orders,
            currency=currency,
        )


class CreateOrderResponseSerializer(serializers.Serializer):
    orders = OrderSerializer(many=True, read_only=True)
    payment_url = serializers.CharField(read_only=True)
    charge_id = serializers.CharField(read_only=True)
    extra_infos = serializers.JSONField(
        required=False,
        help_text=f"""
                gift_details :  {",".join(settings.DIGITAL_PRODUCTS_REQUIRED_KEYS)}  \n
                gift_card : the id of the gift_card

                    """,
    )
    car_id = serializers.IntegerField(required=False)

    # write only fields
    shipping_method = serializers.IntegerField(write_only=True, required=True)
    payment_method = serializers.IntegerField(write_only=True, required=False)
    shipping_address = serializers.IntegerField(write_only=True, required=False)
    pickup_time = serializers.DateTimeField(write_only=True, required=False)


class ProductTagSerializer(ArabicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = ProductTag
        fields = (
            "id",
            "name",
            "name_arabic",
            "text_color",
            "background_color",
        )


class ProductAttributeSerializer(ArabicFieldsMixin, serializers.ModelSerializer):
    attribute_choices = AttributeChoiceSerializer(many=True)

    class Meta:
        model = ProductAttribute
        fields = (
            "id",
            "name",
            "name_arabic",
            "is_mandatory",
            "attribute_choices",
            "type",
            "label",
            "min",
            "max",
        )


class ProductVariantSerializer(ArabicFieldsMixin, serializers.ModelSerializer):
    product_attributes = ProductAttributeSerializer(many=True)
    is_primary = serializers.SerializerMethodField()
    inventory = serializers.SerializerMethodField()
    name_extra = serializers.SerializerMethodField("get_name_extra")
    label_extra = serializers.SerializerMethodField("get_label_extra")

    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "name_extra",
            "label_extra",
            "name",
            "label",
            "sku",
            "product_attributes",
            "is_primary",
            "inventory",
            "image",
            "image_thumbnail_medium",
            "description",
            "is_special",
            "description_arabic",
            "name_arabic",
            "label_arabic",
        )
        extra_kwargs = {"image_thumbnail_medium": {"read_only": True}}

    def get_name_extra(self, obj):
        return obj.name

    def get_label_extra(self, obj):
        return obj.label

    def get_is_primary(self, obj):
        return True if obj.inventories.filter(is_primary=True).exists() else False

    def get_inventory(self, obj):
        inventory = None
        if self.context.get("view"):
            if self.context["view"].kwargs.get("store_pk"):
                store_pk = self.context["view"].kwargs["store_pk"]
                qs = obj.inventories.filter(store=store_pk)
                if qs.exists():
                    inventory = qs.values("price", "discount_percent", "quantity")[0]
        return inventory


class CartItemSerializer(
    InventoryValidationMixin, ArabicFieldsMixin, serializers.ModelSerializer
):
    image = serializers.SerializerMethodField()
    inventory_quantity = serializers.SerializerMethodField()
    is_uncountable = serializers.SerializerMethodField()
    is_available_in_store = serializers.SerializerMethodField()
    product_id = serializers.SerializerMethodField()
    favorite = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    is_multi_variant = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product_variant",
            "product_id",
            "quantity",
            "store",
            "unit_price",
            "total_price",
            "notes",
            "attribute_choices",
            "extra_infos",
            "attribute_choices_total_price",
            "image",
            "inventory_quantity",
            "is_uncountable",
            "is_available_in_store",
            "favorite",
            "is_favorite",
            "is_multi_variant",
        )
        extra_kwargs = {
            "store": {"required": True,},
        }

    def get_is_multi_variant(self, obj):
        product = obj.product_variant.product
        return product.product_variants.all().count() > 1

    def get_is_available_in_store(self, obj):
        if obj.inventory:
            if obj.inventory.quantity:
                return True
        return False

    def get_product_id(self, obj):
        return obj.product_variant.product.id

    def get_inventory_quantity(self, obj):
        if obj.inventory:
            return obj.inventory.quantity
        return None

    def get_is_uncountable(self, obj):
        if obj.inventory:
            return obj.inventory.is_uncountable
        return None

    def validate(self, attrs: typing.Dict) -> typing.Dict:
        return super(CartItemSerializer, self).validate(attrs)

    def get_image(self, obj):
        qs = ProductMedia.objects.filter(product=obj.product_variant.product)
        if qs:
            return qs.first().image.url
        else:
            return None

    def _get_favorite(self, obj):
        user = self.context["request"].user
        favorites = Favorite.objects.favorites_for_object(
            obj.product_variant.product, user
        )
        customization = [obj.product_variant,] + [
            attribute_choice for attribute_choice in obj.attribute_choices.all()
        ]
        for favorite in favorites:
            content_objects = [
                instance.content_object for instance in favorite.extras.all()
            ]
            if set(customization) == set(content_objects):
                return favorite.id
        return None

    def get_favorite(self, obj) -> int:
        return self.favorite

    def get_is_favorite(self, obj) -> bool:
        return self.favorite is not None

    def to_representation(self, instance: CartItem):
        language = (
            True
            if self.context["request"].META.get("HTTP_LANGUAGE", "") == "AR"
            else False
        )
        self.favorite = self._get_favorite(instance)
        data = super().to_representation(instance)
        data["product_variant"] = ProductVariantSerializer(
            instance=instance.product_variant, context=self.context
        ).data
        if language and instance.product_variant.product.name_arabic:
            data["product_name"] = instance.product_variant.product.name_arabic
        else:
            data["product_name"] = instance.product_variant.product.name

        self.context["store"] = instance.store
        data["attribute_choices"] = AttributeChoiceSerializer(
            instance.attribute_choices.all(), many=True, context=self.context
        ).data
        return data

    def create(self, validated_data):
        return super().create(**validated_data)


class CartSerializer(ArabicFieldsMixin, serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = (
            "customer",
            "items",
            "total_price",
            "tax_amount",
            "total_price_with_tax",
            "discount_offer_amount",
            "total_price_with_discount",
            "full_price",
        )
        read_only_fields = (
            "id",
            "total_price",
            "tax_amount",
            "total_price_with_tax",
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        stores = set([item["store"] for item in attrs["items"]])
        if not store_settings.DIFFERENT_STORE_ORDERING and len(stores) > 1:
            raise ValidationError(_("You cannot order from different stores"))
        return attrs

    def update(self, instance, validated_data):
        instance.items.all().delete()
        # update or create instance items
        for item in validated_data["items"]:
            attribute_choices = item.pop("attribute_choices", None)
            logger.info("cart item :", item)
            cart_item, created = CartItem.objects.get_or_create(
                cart=instance,
                pk=item.pop("id", None),
                defaults={
                    "cart": instance,
                    "product_variant": item.pop("product_variant", None),
                    "store": item.pop("store", None),
                    "notes": item.pop("notes", None),
                    "quantity": item.pop("quantity", None),
                },
            )

            if attribute_choices:
                cart_item.attribute_choices.set(attribute_choices)
            cart_item.save()
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        stores = Store.objects.filter(store_items__cart=instance)
        data["store"] = StoreSerializer(stores, many=True, context=self.context).data
        return data


class ProductMediaSerializer(serializers.ModelSerializer):
    image_thumbnail_medium = serializers.ImageField(read_only=True)
    image_thumbnail_small = serializers.ImageField(read_only=True)

    class Meta:
        model = ProductMedia
        fields = (
            "id",
            "is_primary",
            "image",
            "image_thumbnail_small",
            "image_thumbnail_medium",
            "order_value",
        )


class FavoriteMixin:
    def to_representation(self, instance):
        if self.context.get("request"):
            self.favorites = self._get_favorite_object(instance)
        else:
            self.favorites = []
        return super().to_representation(instance)

    def _get_favorite_object(self, instance):
        user = self.context["request"].user
        qs = Favorite.objects.favorites_for_object(instance, user.id).values_list(
            "id", flat=True
        )
        return qs

    def get_favorites(self, obj):
        return self.favorites


class ProductSerializer(ArabicFieldsMixin, FavoriteMixin, serializers.ModelSerializer):
    product_variants = ProductVariantSerializer(many=True)
    product_images = ProductMediaSerializer(many=True, source="images")
    default_variant = ProductVariantSerializer(read_only=True, many=False)
    favorites = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "label",
            "description",
            "product_images",
            "product_variants",
            "default_variant",
            "favorites",
            "name_arabic",
            "description_arabic",
        )

    def to_representation(self, instance: Product):
        data = super().to_representation(instance=instance)
        data["is_favorite"] = len(self.favorites) > 0
        return data


class ProductSearchSerializer(
    ArabicFieldsMixin, FavoriteMixin, serializers.ModelSerializer
):
    is_snoozed = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "name_arabic",
            "slug",
            "description",
            "description_arabic",
            "is_snoozed",
            "is_available",
        )

    def get_store_id(self):
        return self.context["view"].kwargs["store_pk"]

    def get_inventory_for_store(self, product, store_id):
        if store_id:
            return product.get_inventory(store_id)
        return None

    def get_is_snoozed(self, obj):
        store_id = self.get_store_id()
        inventory = self.get_inventory_for_store(obj, store_id)
        return obj.is_snoozed(store_id=store_id) if inventory else False

    def get_is_available(self, obj):
        store_id = self.get_store_id()
        inventory = self.get_inventory_for_store(obj, store_id)
        return bool(inventory and (inventory.quantity or inventory.is_uncountable))


class ProductListSerializer(ArabicFieldsMixin, serializers.ModelSerializer):
    product_images = ProductMediaSerializer(many=True, source="images")

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "name_arabic",
            "slug",
            "label",
            "label_arabic",
            "description",
            "description_arabic",
            "product_images",
            "type",
        )


class SubCategorySerializer(ArabicFieldsMixin, serializers.ModelSerializer):
    products = ProductListSerializer(many=True)
    image_thumbnail_medium = serializers.ImageField(read_only=True)
    image_thumbnail_small = serializers.ImageField(read_only=True)
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "name_arabic",
            "description",
            "description_arabic",
            "is_active",
            "products",
            "image",
            "image_thumbnail_medium",
            "image_thumbnail_small",
            "parent",
            "is_available",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

    def get_is_available(self, obj) -> bool:
        store_id = self.context["request"].query_params.get("store", None)
        if store_id:
            for availability_hours in obj.parent.availability_hours.all():
                if availability_hours.category == obj.parent:
                    return (
                        availability_hours.from_hour
                        <= localtime(now()).time()
                        <= availability_hours.to_hour
                    )
        return False


class CategorySerializer(ArabicFieldsMixin, serializers.ModelSerializer):
    products = ProductListSerializer(many=True)
    subcategories = SubCategorySerializer(many=True, read_only=True)
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "name_arabic",
            "description",
            "description_arabic",
            "products",
            "is_active",
            "subcategories",
            "parent",
            "image",
            "image_thumbnail_medium",
            "image_thumbnail_small",
            "is_available",
        )

    def get_is_available(self, obj) -> bool:
        store_id = self.context["request"].query_params.get("store", None)
        if store_id:
            for availability_hours in obj.availability_hours.all():
                if availability_hours.category == obj:
                    return (
                        availability_hours.from_hour
                        <= localtime(now()).time()
                        <= availability_hours.to_hour
                    )
        return False


class FeedbackConfigSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False)
    attribute = serializers.CharField(read_only=True)

    class Meta:
        model = FeedbackConfig
        fields = ("id", "attribute", "attribute_label", "values")


class FeedbackAttributeSerializer(serializers.ModelSerializer):
    config = FeedbackConfigSerializer(many=False, read_only=True)
    attribute = serializers.CharField(write_only=True)

    class Meta:
        model = FeedbackAttribute
        fields = ("attribute", "config", "value", "review")

    # TODO: do we need validations when creating the value


class FeedbackSerializer(serializers.ModelSerializer):
    attributes = FeedbackAttributeSerializer(many=True, required=False)

    class Meta:
        model = Feedback
        fields = (
            "id",
            "attributes",
            "notes",
            "review",
        )

    def validate(self, attrs: typing.Dict):
        # Validate Order Status
        if self.instance.status not in [
            Order.OrderStatus.PAID,
            Order.OrderStatus.CANCELLED,
        ]:
            raise serializers.ValidationError(
                _("The Order must be PAID or CANCELLED to give a feedback")
            )
        return attrs

    def update(self, instance: Order, validated_data: typing.Dict):
        user = self.context["request"].user
        attributes = validated_data.pop("attributes", [])
        feedback = Feedback.objects.create(
            order=self.instance, user=user, **validated_data
        )

        for attr in attributes:
            feedback.attributes.create(**attr)
        feedback.order.save()
        return feedback


class InventorySerializer(ArabicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = (
            "id",
            "variant",
            "store",
            "quantity",
            "price",
            "plu",
            "preparation_time",
            "discount_percent",
            "discounted_price",
            "is_primary",
        )

    def to_representation(self, instance):

        data = super(InventorySerializer, self).to_representation(instance)
        data["variant"] = ProductVariantSerializer(
            instance=instance.variant, context=self.context
        ).data
        return data


class PhoneContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneContact
        fields = (
            "id",
            "national_number",
            "country_code",
            "is_default",
            "is_active",
        )


class StoreSerializer(ArabicFieldsMixin, FavoriteMixin, serializers.ModelSerializer):

    opening_hours = serializers.SerializerMethodField()
    phone_contacts = serializers.SerializerMethodField()
    in_range_delivery = serializers.SerializerMethodField()
    is_closed = serializers.SerializerMethodField()
    favorites = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    address_line = serializers.SerializerMethodField()
    shipping_methods = ShippingMethodSerializer(many=True, read_only=True)
    distance = serializers.SerializerMethodField()
    current_day_opening_hours = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = (
            "id",
            "name",
            "address",
            "address_line",
            "location",
            "distance",
            "is_active",
            "currency",
            "minimum_order_amount",
            "delivery_charges",
            "shipping_methods",
            "min_free_delivery_amount",
            "opening_hours",
            "in_range_delivery",
            "is_closed",
            "favorites",
            "is_favorite",
            "created_at",
            "updated_at",
            "phone_contacts",
            "current_day_opening_hours",
            "image",
            "busy_mode",
            "name_arabic",
        )
        extra_kwargs = {
            "image": {"read_only": True, "required": False},
        }

    def get_is_closed(self, obj):
        if obj.busy_mode:
            return True
        current_time = localtime(now())
        current_op_hour = obj.current_opening_hours
        if current_op_hour:
            from_hour = current_op_hour.from_hour
            to_hour = current_op_hour.to_hour
            if current_time.tzinfo.zone != "Asia/Dubai":
                if obj.currency == "AED":
                    try:
                        current_time += timedelta(hours=1)
                    except Exception as e:
                        logger.info(
                            f"The fix for UAE stores timezone failed due to this error {e}"
                        )

            if current_op_hour.is_open_after_midnight:
                return True if to_hour < current_time.time() < from_hour else False

            if current_op_hour.always_open:
                return False
            return not from_hour <= current_time.time() <= to_hour
        return True

    def get_in_range_delivery(self, obj):
        user_location = self.context["request"].query_params.get("point")
        in_range_method = False
        for shipping_method in obj.shipping_methods.all():
            if shipping_method.type == ShippingMethod.ShippingType.DELIVERY:
                in_range_method = True
                break
        if not in_range_method:
            return True
        if user_location and obj.poly:
            long, lat = user_location.split(",")
            return obj.poly.contains(Point(float(long), float(lat)))

    def get_opening_hours(self, obj):
        opening_hours = sorted(
            [op_hour for op_hour in obj.opening_hours.all() if not op_hour.always_open],
            key=lambda op_hour: op_hour.weekday,
        )
        always_open_op_hours = sorted(
            [op_hour for op_hour in obj.opening_hours.all() if op_hour.always_open],
            key=lambda op_hour: op_hour.weekday,
        )
        formatted_hours = []
        if len(always_open_op_hours) > 0:
            if len(always_open_op_hours) > 1:
                formatted_hours.append(
                    f"{calendar.day_name[always_open_op_hours[0].weekday - 1]} - {calendar.day_name[always_open_op_hours[-1].weekday - 1]} 24 hours"
                )
            else:
                formatted_hours.append(
                    f"{calendar.day_name[always_open_op_hours[0].weekday - 1]} 24 hours"
                )
        if len(opening_hours) > 0:
            day_1 = calendar.day_name[opening_hours[0].weekday - 1]
            day_2 = None
            for i in range(len(opening_hours)):
                if not opening_hours[i] == opening_hours[-1]:
                    if (
                        opening_hours[i].from_hour == opening_hours[i + 1].from_hour
                        and opening_hours[i].to_hour == opening_hours[i + 1].to_hour
                    ):
                        day_2 = calendar.day_name[opening_hours[i + 1].weekday - 1]
                        continue
                formatted_days = day_1
                if day_2:
                    formatted_days = f"{formatted_days} - {day_2}"
                formatted_hours.append(
                    f"{formatted_days} {opening_hours[i].from_hour.strftime('%I:%M%p')} - {opening_hours[i].to_hour.strftime('%I:%M%p')}"
                )
                if not opening_hours[i] == opening_hours[-1]:
                    day_1 = calendar.day_name[opening_hours[i + 1].weekday - 1]
        return formatted_hours

    def get_is_favorite(self, obj):
        return len(self.favorites) > 0

    def get_address_line(self, obj):
        language = (
            True
            if self.context["request"].META.get("HTTP_LANGUAGE", "") == "AR"
            else False
        )
        if language:
            if obj.address.address_line_arabic:
                return obj.address.address_line_arabic
        return obj.address.address_line

    def get_distance(self, obj):
        # get the distance between the user location and store location
        user_location = self.context["request"].query_params.get("point")
        if user_location and obj.location:
            unit = "km"
            lat, long = user_location.split(",")
            store_lat, store_long = obj.location.x, obj.location.y
            ds = round(distance((float(lat), float(long)), (store_lat, store_long)), 1)
            if ds < 1:
                ds = int(ds * 1000)
                unit = "m"
            return f"{ds}{unit}"

    def get_phone_contacts(self, obj):
        phone_contacts = obj.phone_contacts.all()
        return PhoneContactSerializer(phone_contacts, many=True).data

    def get_current_day_opening_hours(self, obj):
        current_opening_hours = obj.current_opening_hours
        if current_opening_hours:
            if current_opening_hours.always_open:
                op_hour = "24 hours"
            else:
                from_hour = current_opening_hours.from_hour.strftime("%I:%M%p")
                to_hour = current_opening_hours.to_hour.strftime("%I:%M%p")
                op_hour = f"{from_hour} - {to_hour}"
        else:
            op_hour = f"{settings.DEFAULT_OPENING_HOURS[0]['from_hour']} - {settings.DEFAULT_OPENING_HOURS[0]['to_hour']}"
        return op_hour

    def to_representation(self, instance):
        return super().to_representation(instance)


class PaymentMethodSerializer(ArabicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = (
            "id",
            "payment_provider",
            "name",
            "name_arabic",
            "description",
            "description_arabic",
        )


class PaymentSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        fields = ("id", "method", "orders", "amount", "currency", "payment_post_at")


class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = (
            "id",
            "rate",
            "name",
            "value",
            "country",
        )


class StoreListSerializer(ArabicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"


class GenericSerializer(serializers.Serializer):
    """
    A generic serializer that automatically selects the appropriate serializer
    for a given instance.

    The `to_representation` method uses the `get_serializer_for_instance` method
    to determine which serializer to use for a given instance. If the serializer
    class is found, it returns the representation of the instance using that
    serializer. Otherwise, it raises a `NameError`.
    """

    def to_representation(self, value):
        context = self.context
        serializer_class = self.get_serializer_for_instance(value)
        return serializer_class(context=context).to_representation(value)

    def get_serializer_for_instance(self, instance):
        serializer_class = instance.__class__.__name__
        return import_string(
            store_settings.FAVORITES_SERIALIZERS_PATHS[serializer_class]
        )


def get_favorite_extras_models():
    extras_list = []
    for key, value in settings.FAVORITE_TYPES.items():
        if "extras" in value:
            extras_list.extend(value["extras"].keys())
    return extras_list


class FavoriteExtraSerializer(ArabicFieldsMixin, serializers.ModelSerializer):
    content_object = GenericSerializer(read_only=True)
    object_id = serializers.IntegerField(min_value=1)
    object_type = serializers.ChoiceField(
        write_only=True, choices=get_favorite_extras_models()
    )

    class Meta:
        model = FavoriteExtra
        fields = (
            "id",
            "content_object",
            "object_id",
            "object_type",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        extras = get_favorite_extras_models()
        model_name = instance.content_type.model
        for extra in extras:
            if model_name == extra.lower():
                data["object_type"] = extra
                break
        return data


class FavoriteSerializer(ArabicFieldsMixin, serializers.ModelSerializer):
    content_object = GenericSerializer(read_only=True)
    extras = FavoriteExtraSerializer(many=True)
    object_id = serializers.IntegerField(min_value=1, required=False)
    object_type = serializers.ChoiceField(
        write_only=True,
        choices=list(store_settings.FAVORITE_TYPES.keys()),
        required=False,
    )
    is_available_in_store = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = (
            "id",
            "content_object",
            "extras",
            "object_id",
            "extra_info",
            "object_type",
            "name",
            "name_arabic",
            "is_available_in_store",
        )
        extra_kwargs = {
            "name": {"required": True},
        }

    def get_is_available_in_store(self, obj):
        store_id = self.context["request"].query_params.get("store")
        type = self.context["request"].query_params.get("type")
        if type == "Product" and store_id:
            content_type = ContentType.objects.get_for_model(ProductVariant)
            try:
                extra = obj.extras.get(content_type=content_type)
                inventory = extra.content_object.inventories.get(store=store_id)
                if inventory.is_snoozed:
                    return False
                else:
                    if inventory.is_uncountable:
                        return True
                    return False
            except ObjectDoesNotExist:
                return False
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        model_name = instance.content_type.model
        for favorite in store_settings.FAVORITE_TYPES.keys():
            if model_name == favorite.lower():
                data["object_type"] = favorite
                break
        return data

    def _lookup_validation(self, data):
        extra_info = data.get("extra_info", None)
        content_type = ContentType.objects.get_for_model(data["content_object"])
        queryset = Favorite.objects.filter(
            content_type=content_type,
            object_id=data["content_object"].id,
            user=self.context["request"].user,
        ).prefetch_related("extras")
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            for favorite in queryset:
                content_objects = [
                    instance.content_object for instance in favorite.extras.all()
                ]
                if (
                    set(data["extras"]) == set(content_objects)
                    and favorite.extra_info == extra_info
                ):
                    raise serializers.ValidationError(
                        _(f"You cannot favorite the same item twice")
                    )

    def get_object(self, model: models.Model, id: int):
        try:
            object = model.objects.get(pk=id)
            return object
        except model.DoesNotExist:
            raise serializers.ValidationError(
                _(f"{model.__name__} with the id of {id} does not exist")
            )

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        extras_data = {}
        if self.instance is None:
            object_type = validated_data["object_type"]
            object_type_model = import_string(
                store_settings.FAVORITE_TYPES[object_type]["path"]
            )
            object_instance = get_object_or_404(
                object_type_model, pk=validated_data["object_id"]
            )
        else:
            # when update
            model_name = self.instance.content_type.model
            for favorite in store_settings.FAVORITE_TYPES.keys():
                if model_name == favorite.lower():
                    object_type = favorite
            object_instance = self.instance.content_object

        for extra in validated_data["extras"]:
            if (
                extra["object_type"]
                not in store_settings.FAVORITE_TYPES[object_type]["extras"]
            ):
                raise serializers.ValidationError(
                    _(f"{extra['object_type']} Cannot be extra of {object_type}")
                )
            extra_object_type = extra["object_type"]
            extras_data.setdefault(
                extra_object_type,
                {
                    "model": import_string(
                        store_settings.FAVORITE_TYPES[object_type]["extras"][
                            extra_object_type
                        ]["path"]
                    ),
                    "ids": [],
                },
            )
            extras_data[extra_object_type]["ids"].append(extra["object_id"])

        extras = []
        for key, value in extras_data.items():
            type = store_settings.FAVORITE_TYPES[object_type]["extras"][key]["type"]
            if len(value["ids"]) > 1 and type == store_settings.SIGNLE_FAVORITE_EXTRA:
                raise serializers.ValidationError(_(f"Cannot set multiple {key}s"))
            for id in value["ids"]:
                extras.append(
                    self.get_object(value["model"], id)
                )  # get objects of extras instead of ids
        extras = list(set(extras))  # remove duplicated extras
        validated_data = {
            "content_object": object_instance,
            "extras": extras,
            "name": validated_data["name"],
            "extra_info": validated_data.get("extra_info", None),
        }
        self._lookup_validation(validated_data)
        return validated_data

    def create(self, validated_data):
        try:
            favorite = Favorite.add_favorite(
                content_object=validated_data["content_object"],
                user=self.context["request"].user,
                name=validated_data["name"],
                extra_info=validated_data["extra_info"],
                extras=validated_data["extras"],
            )
        except ValidationError as e:
            raise serializers.ValidationError(detail=e.message_dict)
        return favorite

    def update(self, instance, validated_data):
        try:
            favorite = instance.update_favorite(
                validated_data["name"],
                validated_data["extra_info"],
                validated_data["extras"],
            )
        except ValidationError as e:
            raise serializers.ValidationError(detail=e.message_dict)
        return favorite


class WalletMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletMedia
        fields = "__all__"


class WalletSerializer(ArabicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = [
            "id",
            "user",
            "currency",
            "balance",
            "name",
            "name_arabic",
            "media_image",
            "image_url",
        ]
        extra_kwargs = {
            "user": {"read_only": True},
            "currency": {"read_only": True},
        }


class WalletTopUpSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=1, required=True, write_only=True
    )
    payment_method = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=PaymentMethod.objects.filter(
            payment_provider__in=[
                store_settings.TAP_CREDIT_CARD,
                store_settings.TAP_KNET,
                store_settings.TAP_ALL,
                store_settings.APPLE_PAY,
                store_settings.GOOGLE_PAY,
                store_settings.MADA,
                store_settings.BENEFIT,
                store_settings.STRIPE,
            ]
        ),
        required=True,
    )
    extra_infos = serializers.JSONField(required=False, write_only=True)
    payment_url = serializers.CharField(read_only=True)
    charge_id = serializers.CharField(read_only=True)

    def top_up_wallet(self, wallet):
        amount = self.validated_data["amount"]
        payment_method = self.validated_data["payment_method"]
        extra_infos = self.validated_data.get("extra_infos", {})
        return wallet.top_up_wallet(
            amount=amount, payment_method=payment_method, extra_infos=extra_infos
        )


class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = [
            "id",
            "type",
            "amount",
            "created_at",
            "wallet",
            "is_cashback",
            "is_refund",
        ]


class GroupedWalletTransactionListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        result_dict = OrderedDict()
        for wallettransaction in data:
            year = wallettransaction.created_at.year
            month = wallettransaction.created_at.month
            title = f"{datetime(year, month, 1).strftime('%b')}, {year}"

            if title not in result_dict:
                result_dict[title] = {"title": title, "data": []}

            result_dict[title]["data"].append(
                self.child.to_representation(wallettransaction)
            )

        return list(result_dict.values())


class WalletTransactionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = [
            "id",
            "type",
            "amount",
            "created_at",
            "wallet",
            "is_cashback",
            "is_refund",
        ]
        list_serializer_class = GroupedWalletTransactionListSerializer


class ReorderSerializer(serializers.Serializer):
    force_cart = serializers.BooleanField(default=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        order = self.context["view"].get_object()
        cart = self.context["request"].user.cart
        stores = Store.objects.filter(store_items__cart=cart).distinct()
        if attrs["force_cart"]:
            cart.items.all().delete()
        elif stores.exists():
            if stores[0] != order.store or stores.count() > 1:
                raise ValidationError(
                    _("Your cart contains items from different store")
                )
        return attrs


class OrderDataSerializer(serializers.ModelSerializer):
    """
    This class takes an Order object and returns a dictionary of initialization data
    """

    store_name = serializers.SerializerMethodField()
    customer_email = serializers.SerializerMethodField()
    payment_method_name = serializers.SerializerMethodField()
    shipping_address = serializers.SerializerMethodField()
    shipping_method_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "store_name",
            "customer_email",
            "payment_method_name",
            "shipping_method_name",
            "shipping_address",
        )

    def get_store_name(self, obj):
        return obj.store.name if obj.store else None

    def get_customer_email(self, obj):
        return obj.customer.email if obj.customer else None

    def get_payment_method_name(self, obj):
        return obj.payment_method.name if obj.payment_method else None

    def get_shipping_address(self, obj):
        return obj.shipping_address.address_line if obj.shipping_address else None

    def get_shipping_method_name(self, obj):
        return obj.shipping_method.name if obj.shipping_method else None


class PartnerOTPRequestSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = PartnerOTPAuth
        exclude = ("user", "otp", "partner")

    def _validate_old_valid_verification_code(self, attrs):
        # Validate there is unused OTP code
        timeout = now() - timedelta(seconds=getattr(settings, "OTP_TIMEOUT", 3 * 60))
        qs = PartnerOTPAuth.objects.filter(
            created_at__gte=timeout, email=attrs["email"]
        )
        if qs.exists():
            # TODO: Add a mechanism to force a new code request
            # with a field called "force" with checking that he didn't call this api to many times
            seconds_left = (
                timedelta(seconds=getattr(settings, "OTP_TIMEOUT", 3 * 60))
                - (now() - qs.last().created_at)
            ).total_seconds()
            minutes_left = int(seconds_left) // 60 or 1
            raise serializers.ValidationError(
                _(
                    "We sent a verification code please wait for "
                    "{minutes} minutes; before requesting a new code."
                ).format(minutes=minutes_left)
            )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        try:
            partner_auth = PartnerAuth(attrs["email"])
        except ValidationError as e:
            raise serializers.ValidationError(detail=e.messages)
        partner = partner_auth.partner
        if partner.auth_method != Partner.AuthMethods.OTP:
            raise serializers.ValidationError(
                _(f"{partner.name} does not support OTP as Auth Method")
            )
        self._validate_old_valid_verification_code(attrs)
        attrs["partner"] = partner
        return attrs

    def create(self, validated_data):
        user = self.context["view"].request.user
        otp = OneTruePairing.objects.create(
            user=user, usage=OneTruePairing.Usages.auth, email=validated_data["email"]
        )
        partner_otp_auth = PartnerOTPAuth.objects.create(
            user=self.context["view"].request.user,
            partner=validated_data["partner"],
            otp=otp,
            email=validated_data["email"],
        )
        return partner_otp_auth


class PartnerSerializer(ArabicFieldsMixin, serializers.ModelSerializer):
    discount = DiscountSerializer()
    stores = StoreListSerializer(many=True)

    class Meta:
        model = Partner
        fields = (
            "id",
            "name",
            "stores",
            "auth_method",
            "country",
            "discount",
            "name_arabic",
        )


class PartnerAuthInfoSerializer(ArabicFieldsMixin, serializers.ModelSerializer):
    partner = PartnerSerializer(read_only=True)
    promotion_code = serializers.IntegerField(write_only=True, required=False)
    otp_code = serializers.IntegerField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=True)

    class Meta:
        model = PartnerAuthInfo
        fields = (
            "id",
            "user",
            "email",
            "otp_code",
            "promotion_code",
            "partner",
            "authentication_expires",
            "status",
            "created_at",
            "updated_at",
        )
        extra_kwargs = {
            "user": {"read_only": True},
            "email": {"read_only": True},
            "status": {"read_only": True},
            "authentication_expires": {"read_only": True},
        }

    def _validate_partner_auth_method(self, attrs):
        partner = attrs["partner"]
        user = self.context["view"].request.user
        if partner.auth_method == Partner.AuthMethods.OTP:
            otp_code = attrs.get("otp_code", None)
            if otp_code == None:
                raise serializers.ValidationError(_("OTP code is required"))
            timeout = now() - timedelta(
                seconds=getattr(settings, "OTP_TIMEOUT", 3 * 60)
            )
            try:
                otp = OneTruePairing.objects.filter(
                    verification_code=otp_code,
                    status=OneTruePairing.Statuses.init,
                    created_at__gte=timeout,
                ).get(
                    email=attrs["email"], partner_otp_auth__partner=partner, user=user,
                )
                self.context["otp"] = otp
            except ObjectDoesNotExist as e:
                raise serializers.ValidationError(
                    _(f"Invalid verification code.")
                ) from e

        elif partner.auth_method == Partner.AuthMethods.CODE:
            promotion_code = attrs.get("promotion_code", None)
            if promotion_code == None:
                raise serializers.ValidationError(_("Promotion code is required"))
            elif not partner.promotion_code:
                logger.error(f"{partner.name} does not have promotion code")
                raise serializers.ValidationError(_("Promotion code is not working"))
            elif partner.promotion_code != promotion_code:
                raise serializers.ValidationError(_("Promotion code is invalid"))
        return attrs

    def validate(self, attrs):
        attrs = super().validate(attrs)
        try:
            partner_auth = PartnerAuth(attrs["email"])
        except ValidationError as e:
            raise serializers.ValidationError(detail=e.messages)
        attrs["partner"] = partner_auth.partner
        self._validate_partner_auth_method(attrs)
        return attrs

    def create(self, validated_data):
        user = self.context["view"].request.user
        partner = validated_data["partner"]
        if partner.auth_method == Partner.AuthMethods.OTP:
            otp = self.context["otp"]
            otp.status = OneTruePairing.Statuses.used
            otp.save()
        partner_auth_info = PartnerAuthInfo.objects.update_or_create(
            user=user, defaults={"partner": partner, "email": validated_data["email"],},
        )
        return partner_auth_info


class CountryPaymentMethodSerialzier(serializers.ModelSerializer):
    class Meta:
        model = CountryPaymentMethod
        fields = ("id", "country", "payment_methods")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        filter_value = self.context.get("request").query_params.get(
            "order_type", "gift"
        )
        if filter_value == "wallet":
            qs = instance.payment_methods.exclude(payment_provider="wallet")
        else:
            qs = instance.payment_methods

        data["payment_methods"] = PaymentMethodSerializer(
            instance=qs, context=self.context, many=True
        ).data
        return data
