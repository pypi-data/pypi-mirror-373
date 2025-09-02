import logging

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from ob_dj_store.core.stores.managers import (
    CategoryManager,
    ProductManager,
    ProductVariantManager,
)
from ob_dj_store.core.stores.models._store import Store
from ob_dj_store.utils.helpers import (
    category_media_upload_to,
    product_media_upload_to,
    product_variant_media_upload_to,
)
from ob_dj_store.utils.model import DjangoModelCleanMixin

logger = logging.getLogger(__name__)


class Category(DjangoModelCleanMixin, models.Model):
    """
    Represent categories where products can associate with
    """

    is_active = models.BooleanField(default=False)
    name = models.CharField(max_length=200, help_text=_("Name"))
    name_arabic = models.CharField(
        max_length=200, null=True, blank=True, help_text=_("Name in Arabic")
    )
    description = models.TextField(null=True, blank=True)
    description_arabic = models.TextField(null=True, blank=True)
    # parent for allowing subcategories
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )
    image = models.ImageField(upload_to=category_media_upload_to, null=True, blank=True)
    image_thumbnail_small = models.ImageField(
        upload_to="category_media/", null=True, blank=True
    )
    image_thumbnail_medium = models.ImageField(
        upload_to="category_media/", null=True, blank=True
    )
    order_value = models.PositiveSmallIntegerField(
        verbose_name=_("ordering"), default=1
    )
    plu = models.CharField(max_length=40, unique=True, null=True, blank=True)
    external_id = models.CharField(max_length=40, unique=True, null=True, blank=True)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CategoryManager()

    class Meta:
        verbose_name_plural = _("Categories")
        ordering = ("order_value",)

    def __str__(self):
        return f"{self.name}"

    @property
    def subcategories(self):
        return Category.objects.filter(parent=self)


class Menu(DjangoModelCleanMixin, models.Model):
    store = models.OneToOneField(Store, on_delete=models.CASCADE, related_name="menu")
    categories = models.ManyToManyField(Category, related_name="menus")
    name = models.CharField(max_length=255, null=True, blank=True)
    name_arabic = models.CharField(max_length=255, null=True, blank=True)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.store.name} Menu(PK={self.pk})"


class AvailabilityHours(DjangoModelCleanMixin, models.Model):
    """
    AvailabilityHours model linked to Store model and category
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
    from_hour = models.TimeField()
    to_hour = models.TimeField()
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="availability_hours"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="availability_hours"
    )
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("weekday", "from_hour")
        unique_together = (
            "weekday",
            "store",
            "category",
        )

    def __str__(self) -> str:
        return f"Availability Hours for store{self.store}"

    def clean(self) -> None:
        super().clean()
        try:
            if self.store.current_opening_hours.is_open_after_midnight:
                return
        except Exception as e:
            logger.info(f"OpeningHours has no store: {e}")
        if self.from_hour and self.to_hour and (self.from_hour > self.to_hour):
            hours_difference = (24 - self.from_hour.hour) + self.to_hour.hour
            if hours_difference > 24:
                raise ValidationError(
                    "Invalid availability hours: from_hour should be lower than to_hour"
                )
            else:
                raise ValidationError(
                    _("From hour should be lower than To hour"), code="invalid"
                )


class ProductTag(models.Model):
    """
    ProductTag is look up table for indexing and filtering
    """

    name = models.CharField(max_length=500)
    name_arabic = models.CharField(max_length=500, null=True, blank=True)
    text_color = models.CharField(
        default="#000000",
        max_length=7,
        validators=[
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message="Can you please provide a valid color hex !",
            ),
        ],
    )
    background_color = models.CharField(
        default="#000000",
        max_length=7,
        validators=[
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message="Can you please provide a valid color hex !",
            ),
        ],
    )

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self):
        return f"Tag {self.name} (PK={self.pk})"


class Product(DjangoModelCleanMixin, models.Model):
    """
    Product is the main class that hold the basic info about the products
    """

    class ProductTypes(models.TextChoices):
        PHYSICAL = "PHYSICAL", _("physical")
        DIGITAL = "DIGITAL", _("digital")

    name = models.CharField(max_length=200, help_text=_("Name"), unique=True)
    name_arabic = models.CharField(
        max_length=200, null=True, blank=True, help_text=_("Name in arabic"),
    )
    slug = models.SlugField(max_length=255, unique=True)
    label = models.CharField(
        max_length=200, help_text=_("Label"), null=True, blank=True
    )
    label_arabic = models.CharField(
        max_length=200, help_text=_("Label in Arabic"), null=True, blank=True
    )
    description = models.TextField(null=True, blank=True)
    description_arabic = models.TextField(null=True, blank=True)
    # TODO: A product can be assigned to multiple categories
    category = models.ManyToManyField(Category, related_name="products", blank=True,)
    is_active = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    tags = models.ManyToManyField(ProductTag, related_name="products", blank=True)
    type = models.CharField(max_length=32, choices=ProductTypes.choices,)
    plu = models.CharField(max_length=40, unique=True, null=True, blank=True)
    external_id = models.CharField(max_length=40, unique=True, null=True, blank=True)
    order_value = models.PositiveSmallIntegerField(
        verbose_name=_("ordering"), default=1
    )
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductManager()
    # return the default variant

    @property
    def default_variant(self):
        try:
            return self.product_variants.filter(inventories__is_primary=True).first()
        except ObjectDoesNotExist:
            return self.product_variants.first()

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ("order_value",)

    def __str__(self):
        return f"Product {self.name} (PK={self.pk})"

    def get_inventory(self, store_id):
        try:
            # Prefer the primary variant if available
            product_variant = (
                self.product_variants.filter(inventories__is_primary=True).first()
                or self.product_variants.first()
            )
            if not product_variant:
                return None
            return product_variant.inventories.get(store_id=store_id)
        except ObjectDoesNotExist:
            return None

    def is_snoozed(self, store_id):
        try:
            inventory = self.product_variants.first().inventories.get(store=store_id)
        except ObjectDoesNotExist:
            return False
        return inventory.is_snoozed


# TODO: must remove, redundunt
class Attribute(DjangoModelCleanMixin, models.Model):
    """
    Attribute represent a characteristic type for products
    """

    name = models.CharField(max_length=200, help_text=_("Name"))
    name_arabic = models.CharField(
        max_length=200, null=True, blank=True, help_text=_("Name in Arabic")
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Attribute ")
        verbose_name_plural = _("Attributes")

    def __str__(self):
        return f"Attribute {self.name} (PK={self.pk})"


class AttributeChoice(DjangoModelCleanMixin, models.Model):
    """
    AttributeChoice represent a characteristic value for products
    """

    plu = models.CharField(max_length=40, unique=True, null=True, blank=True)
    external_id = models.CharField(max_length=40, unique=True, null=True, blank=True)
    name = models.CharField(max_length=200, help_text=_("Name"))
    name_arabic = models.CharField(
        max_length=200, null=True, blank=True, help_text=_("Name in Arabic")
    )
    description = models.TextField(null=True, blank=True)
    description_arabic = models.TextField(null=True, blank=True)
    order_value = models.PositiveSmallIntegerField(
        verbose_name=_("ordering"), default=1
    )
    is_default = models.BooleanField(default=False)
    label = models.CharField(max_length=200, null=True, blank=True)
    label_arabic = models.CharField(max_length=200, null=True, blank=True)
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_price(self, store):
        try:
            return self.attribute_inventory.get(store=store).price
        except ObjectDoesNotExist:
            raise ValidationError(
                f"AttributeChoice(PK={self.pk} doesnt have inventory at Store(PK={store.pk}))"
            )

    class Meta:
        verbose_name = _("Attribute Choice")
        verbose_name_plural = _("Attribute Choices")
        ordering = ["order_value", "created_at"]

    def __str__(self):
        return f"{self.name}: Attribute Choice  (PK={self.pk})"


class StoreAttributeChoice(models.Model):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="attribute_inventory"
    )
    attribute = models.ForeignKey(
        AttributeChoice, on_delete=models.CASCADE, related_name="attribute_inventory"
    )
    snooze_start_date = models.DateTimeField(
        default=now, help_text=_("When snooze status should begin")
    )
    snooze_end_date = models.DateTimeField(
        default=now, help_text=_("When snooze status should end")
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=3, default=0, help_text=_("Price")
    )

    class Meta:
        verbose_name = _("Store Attribute Choice")
        verbose_name_plural = _("Store Attribute Choices")
        unique_together = (("store", "attribute"),)
        ordering = [
            "price",
        ]

    def __str__(self) -> str:
        return f"StoreProductAttribute(PK={self.pk})"

    @property
    def is_snoozed(self):
        return self.snooze_start_date <= now() <= self.snooze_end_date


class ProductAttribute(DjangoModelCleanMixin, models.Model):
    """
    ProductAttribute represent a characteristic -attribute- with is choices -attribute_choices-
    """

    class Type(models.TextChoices):
        ONE_CHOICE = "ONE_CHOICE", _("one choice")
        MULTIPLE_CHOICES = "MULTIPLE_CHOICES", _("multiple choices")
        LIST_CHOICES = "LIST_CHOICES", _("list choices")
        INCREMENT_CHOICE = "INCREMENT_CHOICE", _("increment choice")

    name = models.CharField(max_length=200, help_text=_("Name"))
    name_arabic = models.CharField(
        max_length=200, null=True, blank=True, help_text=_("Name in Arabic")
    )
    description = models.TextField(null=True, blank=True)
    description_arabic = models.TextField(null=True, blank=True)

    attribute_choices = models.ManyToManyField(
        AttributeChoice, related_name="product_attributes", blank=True
    )
    type = models.CharField(
        max_length=32, default=Type.ONE_CHOICE, choices=Type.choices,
    )
    order_value = models.PositiveSmallIntegerField(
        verbose_name=_("ordering"), default=1
    )
    min = models.PositiveSmallIntegerField(default=1)
    max = models.PositiveSmallIntegerField(default=1)
    is_mandatory = models.BooleanField(default=False)
    plu = models.CharField(max_length=40, unique=True, null=True, blank=True)
    external_id = models.CharField(max_length=40, unique=True, null=True, blank=True)
    label = models.CharField(max_length=200, null=True, blank=True)
    label_arabic = models.CharField(max_length=200, null=True, blank=True)
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Product Attribute")
        verbose_name_plural = _("Product Attributes")
        ordering = ["order_value", "created_at"]

    def __str__(self):
        return f"Product Attribute {self.name} (PK={self.pk})"


class ProductVariant(DjangoModelCleanMixin, models.Model):
    """
    Productvariant is an actual type of a unique product,Every product must have a minimum of one product variantion,
    A productvariant is defined with multiple characteristics stored in `product_attributes`
    """

    name = models.CharField(max_length=200, help_text=_("Name"))
    name_arabic = models.CharField(
        max_length=200, null=True, blank=True, help_text=_("Name in Arabic")
    )
    label = models.CharField(max_length=50, help_text=_("Label"), null=True, blank=True)
    label_arabic = models.CharField(
        max_length=50, help_text=_("Label in arabic"), null=True, blank=True
    )
    description = models.TextField(null=True, blank=True)
    description_arabic = models.TextField(null=True, blank=True)
    product = models.ForeignKey(
        Product, related_name="product_variants", on_delete=models.CASCADE
    )
    product_attributes = models.ManyToManyField(
        ProductAttribute, related_name="product_variants", blank=True
    )
    sku = models.CharField(max_length=100, null=True, blank=True)
    plu = models.CharField(max_length=40, unique=True, null=True, blank=True)
    external_id = models.CharField(max_length=40, unique=True, null=True, blank=True)
    is_special = models.BooleanField(default=False)
    image = models.ImageField(
        upload_to=product_variant_media_upload_to,
        null=True,
        blank=True,
        help_text="optional image field",
    )
    image_thumbnail_medium = models.ImageField(
        upload_to="product_variant_media/", null=True, blank=True
    )
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductVariantManager()

    class Meta:
        verbose_name = _("Product Variation")
        verbose_name_plural = _("Product Variations")

    def __str__(self):
        return f"Variation {self.product.name} {self.name} (PK={self.pk})"

    @property
    def has_inventory(self):
        return self.inventories.count() > 0


class ProductMedia(DjangoModelCleanMixin, models.Model):
    """
    Each Product can have many images to display, but only one primary
    """

    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE,
        verbose_name=_("product"),
    )
    is_primary = models.BooleanField(default=False)
    image = models.ImageField(upload_to=product_media_upload_to)
    image_thumbnail_small = models.ImageField(
        upload_to="product_media/", null=True, blank=True
    )
    image_thumbnail_medium = models.ImageField(
        upload_to="product_media/", null=True, blank=True
    )
    order_value = models.PositiveSmallIntegerField(
        verbose_name=_("ordering"), default=1
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_unique_primary_image",
                fields=("product_id", "is_primary"),
                condition=models.Q(is_primary=True),
            ),
        ]
        ordering = ("order_value",)
        verbose_name = _("product media")
        verbose_name_plural = _("Product medias")

    @property
    def name(self):
        return f"{self.product.name}_{self.order_value}"

    def save(self, *args, **kwargs):
        # If the current instance is set as primary, unset any existing primary images for the product
        if self.is_primary:
            ProductMedia.objects.filter(product=self.product, is_primary=True).update(
                is_primary=False
            )
        elif not ProductMedia.objects.filter(
            product=self.product, is_primary=True
        ).exists():
            # If there are no primary images for the product, set the current instance as primary
            self.is_primary = True
        super(ProductMedia, self).save(*args, **kwargs)
