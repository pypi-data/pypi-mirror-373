import logging
import typing

from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from ob_dj_store.core.stores.managers import (
    CountryPaymentMethodManager,
    PaymentMethodManager,
    ShippingMethodManager,
    StoreManager,
)
from ob_dj_store.core.stores.utils import validate_currency
from ob_dj_store.utils.helpers import store_media_upload_to
from ob_dj_store.utils.model import DjangoModelCleanMixin

logger = logging.getLogger(__name__)


class ShippingMethod(models.Model):
    """
    Decides how orders should be delivered to the customer.
    """

    class ShippingType(models.TextChoices):
        DRIVE_THROUGH = "DRIVE_THROUGH"
        TAKEAWAY = "TAKEAWAY"
        DELIVERY = "DELIVERY"

    class ShippingFeeOptions(models.IntegerChoices):
        """
        Decides how the shipping fees should be calculated.
        """

        FIXED = 1, _("Fixed")
        PER_DISTANCE = 2, _("per distance")
        PER_WEIGHT = 3, _("per weight")

    type = models.CharField(
        max_length=30, choices=ShippingType.choices, default=ShippingType.DELIVERY
    )
    shipping_fee_option = models.IntegerField(
        choices=ShippingFeeOptions.choices, default=1
    )
    name = models.CharField(max_length=200, help_text=_("Name"))
    name_arabic = models.CharField(
        max_length=200, null=True, blank=True, help_text=_("Name in arabic")
    )

    description = models.TextField(null=True, blank=True)
    description_arabic = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    shipping_fee = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
    )
    order_value = models.PositiveSmallIntegerField(
        verbose_name=_("ordering"), default=1
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ShippingMethodManager()

    class Meta:
        verbose_name_plural = _("Shipping Methods")
        verbose_name = _("Shipping Method")
        ordering = ("order_value",)

    def __str__(self):
        return f"Shipping Method {self.name} (PK={self.pk})"


class PaymentMethod(models.Model):
    """
    Payment methods are provided to the customer to select the kind of how
    products are paid.
    """

    payment_provider = models.CharField(
        max_length=20, choices=settings.PAYMENT_PROVIDER_CHOICES, default="cod",
    )
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=200, help_text=_("Name"))
    name_arabic = models.CharField(
        max_length=200, null=True, blank=True, help_text=_("Name")
    )
    description = models.TextField(null=True, blank=True)
    description_arabic = models.TextField(null=True, blank=True)
    order_value = models.PositiveSmallIntegerField(
        verbose_name=_("ordering"), default=1
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PaymentMethodManager()

    class Meta:
        verbose_name_plural = _("Payment Methods")
        verbose_name = _("Payment Method")
        ordering = ("order_value",)

    def __str__(self):
        return f"Payment Method {self.name} (PK={self.pk})"


class CountryPaymentMethod(DjangoModelCleanMixin, models.Model):
    country = CountryField(unique=True)
    payment_methods = models.ManyToManyField(PaymentMethod, related_name="countries")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CountryPaymentMethodManager()

    def __str__(self) -> str:
        return f"Country {self.country} (PK={self.pk})"

    class Meta:
        verbose_name_plural = _("Countries's Payment Methods")
        verbose_name = _("Country's Payment Methods")


class Store(DjangoModelCleanMixin, models.Model):
    name = models.CharField(max_length=100)
    name_arabic = models.CharField(null=True, blank=True, max_length=100)
    address = models.ForeignKey(
        "stores.address", on_delete=models.PROTECT, related_name="stores"
    )
    location = models.PointField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    poly = models.PolygonField(null=True, blank=True)
    shipping_methods = models.ManyToManyField(
        ShippingMethod,
        related_name="shipping_methods",
        blank=True,
        help_text=_("Shipping methods within the store"),
    )
    pickup_addresses = models.ManyToManyField(
        "stores.address", related_name="pickup_stores", blank=True,
    )
    payment_methods = models.ManyToManyField(
        PaymentMethod,
        related_name="stores",
        blank=True,
        help_text=_("Payment methods within the store"),
    )
    minimum_order_amount = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        default=10,
        help_text=_("Minimum order amount allowed"),
    )
    delivery_charges = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        default=0,
        help_text=_("This is the shipping cost for the store"),
    )
    min_free_delivery_amount = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        default=0,
        help_text=_("This is the min price to get a free delivery"),
    )
    image = models.ImageField(upload_to=store_media_upload_to, null=True, blank=True)
    currency = models.CharField(
        max_length=3, default="KWD", validators=[validate_currency,],
    )
    busy_mode = models.BooleanField(default=False)
    is_digital = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = StoreManager()

    class Meta:
        verbose_name_plural = _("Stores")
        verbose_name = _("Store")

    def __str__(self) -> typing.Text:
        return f"Store {self.name} (PK={self.pk})"

    @property
    def current_opening_hours(self):
        return next(
            (x for x in self.opening_hours.all() if x.weekday == now().weekday() + 1),
            None,
        )


class OpeningHours(DjangoModelCleanMixin, models.Model):
    """
    OpeningsHours model linked to Store model
    every store has many opening_hours
    """

    class Weekdays(models.IntegerChoices):
        MONDAY = 1, _("Monday")
        TUESDAY = 2, _("Tuesday")
        WEDNESDAY = 3, _("Wednesday")
        THURSDAY = 4, _("Thursday")
        FRIDAY = 5, _("Friday")
        SATURDAY = 6, _("Saturday")
        SUNDAY = 7, _("Sunday")

    class WeekdaysArabic(models.IntegerChoices):
        MONDAY = 1, _("الاثنين")
        TUESDAY = 2, _("الثلاثاء")
        WEDNESDAY = 3, _("الأربعاء")
        THURSDAY = 4, _("الخميس")
        FRIDAY = 5, _("الجمعة")
        SATURDAY = 6, _("السبت")
        SUNDAY = 7, _("الأحد")

    weekday = models.IntegerField(choices=Weekdays.choices)
    weekday_arabic = models.IntegerField(
        null=True, blank=True, choices=WeekdaysArabic.choices
    )

    from_hour = models.TimeField(help_text=_("Opening hours: From hour "))
    to_hour = models.TimeField(help_text=_("Opening hours: To hour "))
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="opening_hours"
    )
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    always_open = models.BooleanField(default=False)
    is_open_after_midnight = models.BooleanField(default=False)

    class Meta:
        ordering = ("weekday", "from_hour")
        unique_together = (
            "weekday",
            "store",
        )

    def __str__(self) -> str:
        return f"Opening hours for store{self.store}"

    def clean(self) -> None:
        super().clean()
        try:
            if self.store:
                return
        except Exception as e:
            logger.info(f"OpeningHours has no store: {e}")

        if self.from_hour and self.to_hour and (self.from_hour > self.to_hour):
            hours_difference = (24 - self.from_hour.hour) + self.to_hour.hour
            if hours_difference > 24:
                raise ValidationError(
                    "Invalid opening hours: from_hour should be lower than to_hour"
                )
            else:
                raise ValidationError(
                    _("From hour should be lower than To hour"), code="invalid"
                )


class PhoneContact(DjangoModelCleanMixin, models.Model):
    """
    PhoneContact model linked to store model
    every store has many phone_contacts
    """

    phone_number = PhoneNumberField(unique=True)
    store = models.ForeignKey(
        "Store", on_delete=models.CASCADE, related_name="phone_contacts"
    )
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = _("PhoneContacts")
        verbose_name = _("PhoneContact")

    def __str__(self) -> str:
        return f"Phone Contacts for store {self.store}"

    @property
    def country_code(self):
        return self.phone_number.country_code

    @property
    def national_number(self):
        return self.phone_number.national_number
