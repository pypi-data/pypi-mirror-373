from urllib.parse import unquote

from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.search import SearchVector
from django.db.models import Prefetch, Q
from django.utils.timezone import now
from django_filters import rest_framework as filters
from rest_framework.exceptions import ValidationError

from config import settings as store_settings
from ob_dj_store.core.stores.models import (
    Category,
    CountryPaymentMethod,
    Favorite,
    Order,
    Partner,
    PartnerAuthInfo,
    PaymentMethod,
    Product,
    ProductVariant,
    Store,
)
from ob_dj_store.core.stores.models._inventory import Inventory
from ob_dj_store.core.stores.models._wallet import Wallet
from ob_dj_store.core.stores.utils import get_currency_by_country, validate_currency


class StoreFilter(filters.FilterSet):
    """Store filters"""

    location = filters.CharFilter(method="by_location")
    shipping_methods_names = filters.CharFilter(method="by_shipping_methods_names")
    search = filters.CharFilter(method="search_filter")
    shipping_methods = filters.Filter(method="by_shipping_methods")
    is_open = filters.BooleanFilter(method="by_open_stores")
    country = filters.CharFilter(method="by_country")

    class Meta:
        model = Store
        fields = [
            "delivery_charges",
            "min_free_delivery_amount",
            "shipping_methods",
            "is_digital",
        ]

    def by_location(self, queryset, name, value):
        return queryset.filter(poly__contains=value)

    def by_country(self, queryset, name, value):
        return queryset.filter(address__country=value)

    def by_shipping_methods_names(self, queryset, name, value):
        return queryset.filter(shipping_methods__name__in=[value,])

    def by_open_stores(self, queryset, name, value):
        if value:
            current_time = now()
            queryset = queryset.filter(
                Q(
                    opening_hours__weekday=current_time.weekday() + 1,
                    opening_hours__from_hour__lte=current_time.time(),
                    opening_hours__to_hour__gte=current_time.time(),
                )
                | Q(
                    opening_hours__weekday=current_time.weekday() + 1,
                    opening_hours__always_open=True,
                )
            )
        return queryset

    def by_shipping_methods(self, queryset, name, value):
        """
        filter stores's shipping methods by ids example: "1,2"
        """
        try:
            ids = [int(v) for v in value.split(",")]
            return queryset.filter(shipping_methods__in=ids)
        except ValueError:
            raise ValidationError("Invalide Value")

    def search_filter(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("name", "address__address_line")
        ).filter(Q(search=value) | Q(search__icontains=value))


class ProductFilter(filters.FilterSet):
    """Product filters"""

    category = filters.CharFilter(method="by_category")
    q = filters.CharFilter(method="filter_search")

    class Meta:
        model = Product
        fields = [
            "is_featured",
            "type",
            "category",
        ]

    def by_category(self, queryset, name, value):
        return queryset.filter(category__name__iexact=value)

    def filter_search(self, queryset, name, value):
        language = self.request.META.get("HTTP_LANGUAGE", "").strip().upper()
        if language == "AR":
            value_ar = unquote(value)
            query = Q(name_arabic__icontains=value_ar) | Q(
                description_arabic__icontains=value_ar
            )
        else:
            query = Q(name__icontains=value) | Q(description__icontains=value)
        qs = queryset.filter(query).distinct()[:5]
        return qs


class VariantFilter(filters.FilterSet):
    """Variant filters"""

    class Meta:
        model = ProductVariant
        fields = [
            "product__name",
            "product__category__name",
        ]


class CategoryFilter(filters.FilterSet):
    """Category filters"""

    store = filters.CharFilter(method="by_store")
    type = filters.ChoiceFilter(choices=Product.ProductTypes.choices, method="by_type")

    class Meta:
        model = Category
        fields = [
            "name",
        ]

    def by_store(self, queryset, name, value):
        queryset = (
            queryset.filter(
                Q(
                    subcategories__products__product_variants__inventories__snooze_start_date__gt=now(),
                    subcategories__products__product_variants__inventories__store=value,
                    subcategories__products__is_active=True,
                    menus__store=value,
                    is_active=True,
                )
                | Q(
                    subcategories__products__product_variants__inventories__snooze_end_date__lt=now(),
                    subcategories__products__product_variants__inventories__store=value,
                    menus__store=value,
                    subcategories__products__is_active=True,
                    is_active=True,
                )
            )
            .prefetch_related(
                Prefetch(
                    "subcategories",
                    queryset=Category.objects.filter(
                        Q(
                            products__product_variants__inventories__snooze_start_date__gt=now(),
                            products__product_variants__inventories__store=value,
                            products__is_active=True,
                            is_active=True,
                        )
                        | Q(
                            products__product_variants__inventories__snooze_end_date__lt=now(),
                            products__product_variants__inventories__store=value,
                            products__is_active=True,
                            is_active=True,
                        )
                    ).distinct(),
                ),
                Prefetch(
                    "subcategories__products",
                    queryset=Product.objects.filter(
                        Q(
                            product_variants__inventories__snooze_start_date__gt=now(),
                            product_variants__inventories__store=value,
                            is_active=True,
                        )
                        | Q(
                            product_variants__inventories__snooze_end_date__lt=now(),
                            product_variants__inventories__store=value,
                            is_active=True,
                        )
                    ).distinct(),
                ),
                "subcategories__products__images",
            )
            .distinct()
        )
        return queryset

    def by_type(self, queryset, name, value):
        return (
            queryset.filter(subcategories__products__type=value,)
            .prefetch_related(
                Prefetch(
                    "subcategories",
                    queryset=Category.objects.filter(
                        is_active=True, products__type=value
                    ).distinct(),
                ),
                Prefetch(
                    "subcategories__products",
                    queryset=Product.objects.filter(is_active=True,).distinct(),
                ),
            )
            .distinct()
        )


class OrderFilter(filters.FilterSet):
    """Order filters"""

    class Meta:
        model = Order
        fields = [
            "status",
        ]


class InventoryFilter(filters.FilterSet):
    """Category filters"""

    class Meta:
        model = Inventory
        fields = [
            "store",
            "variant",
        ]


class FavoriteFilter(filters.FilterSet):

    store = filters.CharFilter(method="by_store")

    class Meta:
        model = Favorite
        fields = ["store"]

    def by_store(self, queryset, name, value):
        products_ids = Product.objects.filter(
            product_variants__inventories__store__pk=value
        ).values_list("id", flat=True)
        content_type = ContentType.objects.get_for_model(Product)
        return queryset.filter(content_type=content_type, object_id__in=products_ids,)


class PaymentMethodFilter(filters.FilterSet):
    store = filters.CharFilter(method="by_store")
    is_digital = filters.BooleanFilter(method="by_digital")
    country = filters.CharFilter(method="by_country")

    class Meta:
        models = PaymentMethod

    def by_store(self, queryset, name, value):
        return queryset.filter(stores=value)

    def by_digital(self, queryset, name, value):
        if value:
            return queryset.filter(
                payment_provider__in=store_settings.DIGITAL_PAYMENT_METHODS
            )
        return queryset

    def by_country(self, queryset, name, value):
        currency = get_currency_by_country(value)
        if value:
            queryset = queryset.filter(currency=currency)
        return queryset


class WalletFilter(filters.FilterSet):
    currency = filters.CharFilter(
        method="by_currency", validators=[validate_currency,],
    )
    country = filters.CharFilter(method="by_country")

    class Meta:
        models = Wallet

    def by_currency(self, queryset, name, value):
        return queryset.filter(currency=value)

    def by_country(self, queryset, name, value):
        if value:
            currency = get_currency_by_country(value)
            return queryset.filter(currency=currency)


class PartnerFilter(filters.FilterSet):
    country = filters.CharFilter(method="by_country")

    class Meta:
        models = Partner

    def by_country(self, queryset, name, value):
        if value:
            return queryset.filter(country=value)


class PartnerAuthInfoFilter(filters.FilterSet):
    class Meta:
        models = PartnerAuthInfo
        fields = [
            "partner",
        ]


class CountryPaymentMethodFilter(filters.FilterSet):
    country = filters.CharFilter(method="by_country")

    class Meta:
        models = CountryPaymentMethod

    def by_country(self, queryset, name, value):
        if value:
            return queryset.filter(country=value)
