from django.contrib import admin

from ob_dj_store.core.stores import models


class OpeningHoursInlineAdmin(admin.TabularInline):
    model = models.OpeningHours
    extra = 1
    fields = [
        "store",
        "weekday",
        "weekday_arabic",
        "from_hour",
        "to_hour",
        "always_open",
        "is_open_after_midnight",
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("store")


class AvailabilityHoursInlineAdmin(admin.TabularInline):
    model = models.AvailabilityHours
    extra = 1
    readonly_fields = ("store",)
    fields = ["store", "weekday", "from_hour", "to_hour"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("store",)


class PhoneContactInlineAdmin(admin.TabularInline):
    model = models.PhoneContact
    extra = 1

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("store")


class AttributeChoiceInlineAdmin(admin.TabularInline):
    model = models.ProductAttribute.attribute_choices.through
    extra = 1


class ProductAttributeInlineAdmin(admin.TabularInline):
    model = models.ProductVariant.product_attributes.through
    extra = 1


class InventoryInlineAdmin(admin.TabularInline):
    model = models.Inventory
    extra = 1
    readonly_fields = (
        "variant",
        "store",
    )
    fields = [
        "store",
        "variant",
        "quantity",
        "price",
        "discount_percent",
        "is_active",
        "is_uncountable",
        "is_deliverable",
        "preparation_time",
        "snooze_start_date",
        "snooze_end_date",
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("store", "variant__product")


class ProductVariantInlineAdmin(admin.TabularInline):
    model = models.ProductVariant
    extra = 1


class OrderHistoryInlineAdmin(admin.TabularInline):
    model = models.OrderHistory
    extra = 1


class ProductMediaInlineAdmin(admin.TabularInline):
    model = models.ProductMedia
    extra = 1


class CartItemInlineAdmin(admin.TabularInline):
    readonly_fields = [
        "unit_price",
    ]
    list_display = [
        "product_variant",
        "quantity",
    ]
    model = models.CartItem


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    extra = 0
    fields = ("product_variant", "quantity", "unit_value", "total_amount", "notes")
    readonly_fields = (
        "unit_value",
        "total_amount",
    )

    def unit_value(self, obj):
        return obj.product_variant.price if obj.product_variant else None


class InventoryOperationInlineAdmin(admin.TabularInline):
    model = models.InventoryOperations
    extra = 1


class PartnerEmailDomainInlineAdmin(admin.TabularInline):
    model = models.PartnerEmailDomain
    extra = 1
