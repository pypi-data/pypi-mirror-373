import logging
import typing

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max, Prefetch, Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.timezone import localtime, now
from django.utils.translation import ugettext_lazy as _
from django_auto_prefetching import AutoPrefetchViewSetMixin, prefetch
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_gis.filters import DistanceToPointOrderingFilter
from rest_framework_nested.viewsets import NestedViewSetMixin

from config import settings as store_settings
from ob_dj_store.apis.stores.filters import (
    CategoryFilter,
    CountryPaymentMethodFilter,
    InventoryFilter,
    OrderFilter,
    PartnerAuthInfoFilter,
    PartnerFilter,
    PaymentMethodFilter,
    ProductFilter,
    StoreFilter,
    VariantFilter,
    WalletFilter,
)
from ob_dj_store.apis.stores.rest.serializers.serializers import (
    CartItemSerializer,
    CartSerializer,
    CategorySerializer,
    CountryPaymentMethodSerialzier,
    CreateOrderResponseSerializer,
    FavoriteSerializer,
    FeedbackSerializer,
    InventorySerializer,
    OrderSerializer,
    PartnerAuthInfoSerializer,
    PartnerOTPRequestSerializer,
    PartnerSerializer,
    PaymentMethodSerializer,
    PaymentSerializer,
    ProductListSerializer,
    ProductSearchSerializer,
    ProductSerializer,
    ProductVariantSerializer,
    ReorderSerializer,
    ShippingMethodSerializer,
    StoreSerializer,
    TaxSerializer,
    WalletMediaSerializer,
    WalletSerializer,
    WalletTopUpSerializer,
    WalletTransactionListSerializer,
    WalletTransactionSerializer,
)
from ob_dj_store.core.stores.gateway.tap.utils import TapException
from ob_dj_store.core.stores.models import (
    AttributeChoice,
    AvailabilityHours,
    Cart,
    CartItem,
    Category,
    CountryPaymentMethod,
    Favorite,
    FeedbackConfig,
    Order,
    Partner,
    PartnerAuthInfo,
    Payment,
    PaymentMethod,
    PhoneContact,
    Product,
    ProductVariant,
    ShippingMethod,
    Store,
    Tax,
    Wallet,
    WalletMedia,
)
from ob_dj_store.core.stores.models._inventory import Inventory

logger = logging.getLogger(__name__)


class StoreView(
    AutoPrefetchViewSetMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = StoreSerializer
    permission_classes = [
        permissions.AllowAny,
    ]
    filterset_class = StoreFilter
    queryset = Store.objects.active()
    distance_ordering_filter_field = "location"
    filter_backends = [DistanceToPointOrderingFilter, DjangoFilterBackend]
    lookup_value_regex = "[0-9]+"

    def get_permissions(self):
        if self.action in ["favorites", "favorite", "recently_ordered_from", "count"]:
            return [
                permissions.IsAuthenticated(),
            ]
        return super(StoreView, self).get_permissions()

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .prefetch_related(
                "shipping_methods",
                "opening_hours",
                Prefetch(
                    "phone_contacts",
                    queryset=PhoneContact.objects.filter(is_active=True).order_by(
                        "-is_default"
                    ),
                ),
            )
        )
        if self.action == "favorites":
            favorite_store_ids = Favorite.objects.favorites_for_model(
                Store, self.request.user
            ).values_list("object_id", flat=True)
            queryset = self.queryset.filter(pk__in=favorite_store_ids)
        # stores that the user has recently ordered from
        if self.action == "recently_ordered_from":
            queryset = (
                queryset.filter(
                    orders__customer=self.request.user,
                    orders__status__in=["PAID", "DELIVERED",],
                )
                .annotate(latest_order_date=Max("orders__created_at"))
                .prefetch_related(
                    Prefetch(
                        "orders",
                        queryset=Order.objects.filter(
                            customer=self.request.user, status__in=["PAID", "DELIVERED"]
                        ).distinct(),
                    )
                )
                .order_by("-latest_order_date")
                .distinct()
            )
        return prefetch(queryset, self.serializer_class)

    @swagger_auto_schema(
        operation_summary="List Stores",
        operation_description="""
            List Stores
        """,
        tags=["Store",],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="List Stores",
        operation_description="""
            List Stores
        """,
        tags=["Store",],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Favorites",
        operation_description="""
            Retrieve user favorite stores
        """,
        tags=["Store",],
    )
    @action(
        detail=False,
        methods=["GET"],
        url_path="favorites",
        serializer_class=StoreSerializer,
    )
    def favorites(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Recently Ordered From",
        operation_description="""
            Stores that the user has recently ordered from
        """,
        tags=["Store",],
    )
    @action(
        detail=False,
        methods=["GET"],
        url_path="recently_ordered_from",
        serializer_class=StoreSerializer,
    )
    def recently_ordered_from(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Retrieve count of store's products",
        operation_description="""
            Retrieve count of store's products
        """,
        tags=["Store",],
    )
    @action(
        detail=True, methods=["GET"], url_path="menu-count",
    )
    def menu_count(self, request, *args, **kwargs):
        store = self.get_object()
        products_ids = Product.objects.filter(
            product_variants__inventories__store=store
        ).values_list("id", flat=True)
        content_type = ContentType.objects.get_for_model(Product)
        favorites_count = (
            Favorite.objects.filter(
                content_type=content_type, object_id__in=products_ids, user=request.user
            ).count()
            if request.user.id
            else 0
        )
        menu = Product.objects.filter(
            product_variants__inventories__store=store,
            category__isnull=False,
            is_active=True,
        ).distinct()
        data = {
            "favorites_count": favorites_count,
            "menu_count": menu.count(),
            "featured_count": menu.filter(is_featured=True).count(),
        }
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Retrieve count of stores",
        operation_description="""
            Retrieve count of stores (Nearby,previous,favorites)
        """,
        tags=["Store",],
    )
    @action(
        detail=False, methods=["GET"], url_path="count",
    )
    def count(self, request, *args, **kwargs):
        previous_count = (
            super()
            .get_queryset()
            .filter(
                orders__customer=self.request.user,
                orders__status__in=["PAID", "DELIVERED",],
            )
            .distinct()
            .count()
        )
        nearby_count = self.filter_queryset(self.get_queryset()).count()
        favorite_store_ids = Favorite.objects.favorites_for_model(
            Store, self.request.user
        ).values_list("object_id", flat=True)
        favorites_count = self.queryset.filter(pk__in=favorite_store_ids).count()
        data = {
            "previous_count": previous_count,
            "nearby_count": nearby_count,
            "favorites_count": favorites_count,
        }
        return Response(data, status=status.HTTP_200_OK)


class CartView(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    serializer_class = CartSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    queryset = Cart.objects.all()

    def get_object(self):
        return self.request.user.cart

    @swagger_auto_schema(
        operation_summary="Retrieve Customer Cart",
        manual_parameters=[
            openapi.Parameter(
                "store",
                in_=openapi.IN_QUERY,
                description="store id",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        operation_description="""
            Retrieve the current customer's cart /store/cart/me
        """,
        tags=["Cart",],
    )
    def retrieve(self, request, *args, **kwargs):
        store_id = request.query_params.get("store", None)
        instance = self.get_object()

        if store_id and not store_settings.DIFFERENT_STORE_ORDERING:
            store = get_object_or_404(Store, pk=store_id)
            instance.items.update(store=store)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Update Customer Cart",
        operation_description="""
            Updates the current customer's cart /store/cart/me
        """,
        tags=["Cart",],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Validate Customer Cart",
        operation_description="""
            Validate the current customer's cart
        """,
        manual_parameters=[
            openapi.Parameter(
                "store",
                in_=openapi.IN_QUERY,
                description="Store of the order",
                type=openapi.TYPE_INTEGER,
                required=not store_settings.DIFFERENT_STORE_ORDERING,
            ),
        ],
        tags=["Cart",],
    )
    @action(
        methods=["POST"],
        detail=False,
        url_path=r"validate",
        permission_classes=[permissions.IsAuthenticated,],
        serializer_class=OrderSerializer,
    )
    def validate(self, request, *args, **kwargs):
        store_pk = request.data.get("store", None)
        if not store_settings.DIFFERENT_STORE_ORDERING and not store_pk:
            raise ValidationError({"store": "Store field is missing!"})
        if store_pk:
            self.kwargs["store_pk"] = store_pk
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"result": "ok"}, status=status.HTTP_200_OK)


class CartItemView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CartItemSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    queryset = CartItem.objects.all()
    lookup_value_regex = "[0-9]+"

    @swagger_auto_schema(
        operation_summary="Retrieve Cart Item",
        operation_description="""
            Retrieve the current cart's cart item
        """,
        tags=["CartItem",],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Customer Cart Item",
        operation_description="""
            Updates the current customer's cart item
        """,
        tags=["CartItem",],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete Customer Cart Item",
        operation_description="""
            Deletes the current customer's cart item
        """,
        tags=["CartItem",],
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class OrderView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = OrderSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    filterset_class = OrderFilter
    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return CreateOrderResponseSerializer
        return self.serializer_class

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    @swagger_auto_schema(
        operation_summary="Retrieve An Order",
        operation_description="""
            Retrieve an order by id
        """,
        tags=["Order",],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="List Orders",
        operation_description="""
            List Orders
        """,
        tags=["Order",],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a Customer Order",
        operation_description="""
            Create a customer order
        """,
        tags=["Order",],
    )
    def create(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        serializer = OrderSerializer(data=request.data, context=context)
        orders = []
        if serializer.is_valid(raise_exception=True):
            orders, payment_url, charge_id = serializer.save().values()
        orders_data = OrderSerializer(orders, many=True).data
        return Response(
            status=status.HTTP_201_CREATED,
            data={
                "payment_url": payment_url,
                "orders": orders_data,
                "charge_id": charge_id,
            },
        )

    @action(
        methods=["POST"],
        detail=True,
        url_path=r"feedback",
        permission_classes=[permissions.IsAuthenticated,],
    )
    def feedback(
        self, request: Request, pk=None, *args: typing.Any, **kwargs: typing.Any
    ):
        """Action for users to submit a feedback on successful order;"""
        serializer = FeedbackSerializer(
            data=request.data, instance=self.get_object(), context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except FeedbackConfig.DoesNotExist:
            return Response(
                _(
                    "No FeedbackAttribute instance found for the related feedbackconfig attribute."
                ),
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReorderViewSet(
    mixins.CreateModelMixin, viewsets.GenericViewSet,
):
    serializer_class = ReorderSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    queryset = Order.objects.all()
    http_method_names = [
        "post",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(customer=self.request.user)

    @swagger_auto_schema(
        operation_summary="re-order a Customer Order",
        operation_description="""
            re-order a customer order
        """,
        tags=["Order",],
    )
    @action(
        methods=["POST"],
        detail=True,
        url_path=r"",
        permission_classes=[permissions.IsAuthenticated,],
    )
    def reorder(self, request: Request, *args: typing.Any, **kwargs: typing.Any):
        context = self.get_serializer_context()
        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        request.user.cart.fill(self.get_object())
        return Response(status=status.HTTP_200_OK,)


class VariantView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductVariantSerializer
    permission_classes = [
        permissions.AllowAny,
    ]
    filterset_class = VariantFilter
    queryset = ProductVariant.objects.all()

    @swagger_auto_schema(
        operation_summary="List Variants",
        operation_description="""
            List Variants
        """,
        tags=["Variant",],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProductView(
    NestedViewSetMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ProductSerializer
    parent_lookup_kwargs = {
        "store_pk": "product_variants__inventories__store__pk",
    }
    permission_classes = [
        permissions.AllowAny,
    ]
    filterset_class = ProductFilter
    queryset = Product.objects.active()

    def get_serializer_class(self):
        if self.request.query_params.get("q"):
            return ProductSearchSerializer
        return ProductSerializer

    def apply_prefetch(self, queryset):

        qs = queryset.prefetch_related(
            Prefetch(
                "product_variants",
                queryset=ProductVariant.objects.filter(
                    Q(
                        inventories__snooze_start_date__gt=now(),
                        inventories__store__pk=self.kwargs["store_pk"],
                    )
                    | Q(
                        inventories__snooze_end_date__lt=now(),
                        inventories__store__pk=self.kwargs["store_pk"],
                    )
                ).distinct(),
            ),
            Prefetch(
                "product_variants__product_attributes__attribute_choices",
                queryset=AttributeChoice.objects.filter(
                    Q(
                        attribute_inventory__snooze_start_date__gt=now(),
                        attribute_inventory__store__pk=self.kwargs["store_pk"],
                    )
                    | Q(
                        attribute_inventory__snooze_end_date__lt=now(),
                        attribute_inventory__store__pk=self.kwargs["store_pk"],
                    )
                ).distinct(),
            ),
        ).distinct()
        return qs

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related("images",)
        if self.action == "favorites":
            favorite_product_ids = Favorite.objects.favorites_for_model(
                Product, self.request.user
            ).values_list("object_id", flat=True)

            queryset = self.queryset.filter(pk__in=favorite_product_ids)
        queryset = self.apply_prefetch(queryset)
        return queryset

    def get_object(self):
        queryset = super().get_queryset()
        queryset = self.apply_prefetch(queryset)
        pk = self.kwargs.get("pk")
        return get_object_or_404(queryset, pk=pk)

    @swagger_auto_schema(
        operation_summary="Retrieve A Product",
        operation_description="""
            Retrieve a Product by id
        """,
        tags=["Product",],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="List Products",
        operation_description="""
            List Products
        """,
        tags=["Product",],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Favorites",
        operation_description="""
            Retrieve user favorite products
        """,
        tags=["Product",],
    )
    @action(
        detail=False,
        methods=["GET"],
        url_path="favorites",
        serializer_class=ProductListSerializer,
    )
    def favorites(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Add or Remove Product from Favorites",
        operation_description="""
            Add or Remove Product from Favorites
        """,
        tags=["Product",],
    )
    @action(
        detail=True, methods=["GET"], url_path="favorite",
    )
    def favorite(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            Favorite.objects.favorite_for_user(instance, request.user).delete()
        except Favorite.DoesNotExist:
            Favorite.add_favorite(instance, request.user)
        serializer = ProductSerializer(instance=instance, context={"request": request})
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Featured products",
        operation_description="""
            List user's featured products
        """,
        tags=["Product",],
    )
    @action(
        detail=False, methods=["GET"], url_path="featured",
    )
    def featured(self, request, *args, **kwargs):
        instance = self.get_queryset().filter(is_featured=True)
        page = self.paginate_queryset(instance)
        serializer = ProductListSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class CategoryViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    http_method_names = ["get"]
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Category.objects.all()
    filterset_class = CategoryFilter
    lookup_value_regex = "[0-9]+"

    def get_queryset(self):
        store_id = self.request.query_params.get("store", None)
        queryset = super().get_queryset()
        if store_id:
            queryset = queryset.prefetch_related(
                "products__images",
                Prefetch(
                    "availability_hours",
                    queryset=AvailabilityHours.objects.filter(
                        weekday=localtime(now()).weekday() + 1, store=store_id,
                    ),
                ),
            )
        return queryset.filter(is_active=True)

    def get_object(self):
        store_id = self.request.query_params.get("store", None)
        instance_pk = self.kwargs["pk"]
        if not store_id:
            return get_object_or_404(Category, pk=instance_pk, is_active=True)
        try:
            not_in_range = Q(
                product_variants__inventories__snooze_start_date__gt=now(),
                product_variants__inventories__store=store_id,
                is_active=True,
            ) | Q(
                product_variants__inventories__snooze_end_date__lt=now(),
                product_variants__inventories__store=store_id,
                is_active=True,
            )
            product_queryset = Product.objects.filter(not_in_range).distinct()
            instance = self.queryset.prefetch_related(
                Prefetch(
                    "subcategories",
                    queryset=Category.objects.filter(
                        Q(
                            products__product_variants__inventories__snooze_start_date__gt=now(),
                            products__product_variants__inventories__store=store_id,
                            products__is_active=True,
                            is_active=True,
                        )
                        | Q(
                            products__product_variants__inventories__snooze_end_date__lt=now(),
                            products__product_variants__inventories__store=store_id,
                            products__is_active=True,
                            is_active=True,
                        )
                    ).distinct(),
                ),
                Prefetch(
                    "subcategories__products", queryset=product_queryset.distinct(),
                ),
                Prefetch("products", queryset=product_queryset.distinct(),),
                "subcategories__products__images",
            ).get(pk=instance_pk)
        except Category.DoesNotExist:
            raise Http404("No Category matches the given query.")
        return instance

    @method_decorator(
        name="retrieve",
        decorator=swagger_auto_schema(
            operation_summary="Retrieve Category", tags=["Category",],
        ),
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @method_decorator(
        name="list",
        decorator=swagger_auto_schema(
            operation_summary="List Categories", tags=["Category",],
        ),
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class InventoryView(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    serializer_class = InventorySerializer
    permission_classes = [
        permissions.AllowAny,
    ]
    queryset = Inventory.objects.all()
    filterset_class = InventoryFilter

    @method_decorator(
        name="list",
        decorator=swagger_auto_schema(
            operation_summary="List Inventories", tags=["Inventory",],
        ),
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(
        name="retrieve",
        decorator=swagger_auto_schema(
            operation_summary="Retrieve Inventory", tags=["Inventory",],
        ),
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class TransactionsViewSet(
    mixins.ListModelMixin, viewsets.GenericViewSet,
):
    serializer_class = PaymentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    queryset = Payment.objects.all()

    def get_queryset(self):
        return Payment.objects.filter(
            user=self.request.user, status=Payment.PaymentStatus.SUCCESS.value
        ).order_by("-payment_post_at")

    @swagger_auto_schema(
        operation_summary="List Users's Captured Transactions",
        operation_description="""
            List Users's Captured Transactions
        """,
        tags=["payment",],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PaymentMethodViewSet(
    mixins.ListModelMixin, viewsets.GenericViewSet,
):
    serializer_class = PaymentMethodSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    queryset = PaymentMethod.objects.filter(is_active=True)
    filterset_class = PaymentMethodFilter
    lookup_value_regex = "[0-9]+"

    @swagger_auto_schema(
        operation_summary="List Payment Methods",
        operation_description="""
            List Payment methods
        """,
        tags=["Payment Method",],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ShippingMethodViewSet(
    mixins.ListModelMixin, viewsets.GenericViewSet,
):
    serializer_class = ShippingMethodSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    queryset = ShippingMethod.objects.all()

    def get_queryset(self):
        """
        if we get store_pk=0 we fetch all the shipping methods
        """
        if int(self.kwargs["store_pk"]) == 0:
            return ShippingMethod.objects.filter(is_active=True)
        try:
            store = Store.objects.get(pk=self.kwargs["store_pk"])
        except ObjectDoesNotExist:
            raise ValidationError(_(f"Store does not Exist"))
        return store.shipping_methods.filter(is_active=True)

    @swagger_auto_schema(
        operation_summary="List Shipping Methods",
        operation_description="""
            List Shipping methods
        """,
        tags=["Store",],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class TaxViewSet(
    mixins.ListModelMixin, viewsets.GenericViewSet,
):
    serializer_class = TaxSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    queryset = Tax.objects.all()

    @swagger_auto_schema(
        operation_summary="List Taxes",
        operation_description="""
            List Taxes
        """,
        tags=["Tax",],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FavoriteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = FavoriteSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    queryset = Favorite.objects.all()
    #    filterset_class = FavoriteFilter

    def get_queryset(self):
        model = self.request.query_params.get("type")
        if self.action in ["destroy", "update"]:
            return self.queryset.filter(user=self.request.user)
        if not model and model not in store_settings.FAVORITE_TYPES:
            raise ValidationError(_("You must provide the favorite type"))
        self.queryset = Favorite.objects.favorites_for_model(
            eval(model), self.request.user
        )
        return super().get_queryset()

    @swagger_auto_schema(
        operation_summary="List Favorites",
        operation_description="""
            List Favorites
        """,
        manual_parameters=[
            openapi.Parameter(
                "type",
                in_=openapi.IN_QUERY,
                description="Type of the Favorite item",
                type=openapi.TYPE_STRING,
                enum=list(store_settings.FAVORITE_TYPES),
                required=True,
            ),
            openapi.Parameter(
                "store",
                in_=openapi.IN_QUERY,
                description="Store i of favorite products",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        tags=["Favorite",],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retreive Item To Favorites",
        operation_description="""
            Retreive  Item To Favorites
        """,
        tags=["Favorite",],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Add Item To Favorites",
        operation_description="""
            Add  Item To Favorites
        """,
        tags=["Favorite",],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Item From Favorites",
        operation_description="""
            Update  Item From Favorites
        """,
        tags=["Favorite",],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Remove Item From Favorites",
        operation_description="""
            Remove  Item From Favorites
        """,
        tags=["Favorite",],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class WalletViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    filterset_class = WalletFilter
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_queryset(self):
        return Wallet.objects.filter(
            user=self.request.user, is_active=True
        ).select_related("media_image")

    @swagger_auto_schema(
        operation_summary="Get User Wallet",
        operation_description="""
                Get User Wallet
            """,
        tags=["Wallet",],
    )
    def retrieve(
        self, request: Request, *args: typing.Any, **kwargs: typing.Any
    ) -> Response:
        return super().retrieve(request=request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update user wallet",
        operation_description="""
            Update a wallet
        """,
        tags=["Wallet",],
    )
    def partial_update(self, request: Request, *args: typing.Any, **kwargs: typing.Any):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="List User Wallets",
        operation_description="""
                List User Wallets
            """,
        tags=["Wallet",],
    )
    def list(
        self, request: Request, *args: typing.Any, **kwargs: typing.Any
    ) -> Response:
        return super().list(request=request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="top up a wallet",
        operation_description="""
                top up a user wallet with tap payment
            """,
        tags=["Wallet",],
    )
    @action(
        methods=["POST"],
        detail=True,
        url_path="top-up",
        url_name="top-up",
        serializer_class=WalletTopUpSerializer,
    )
    def top_up_wallet(
        self, request: Request, *args: typing.Any, **kwargs: typing.Any
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        try:
            payment_url, charge_id = serializer.top_up_wallet(instance)
        except TapException as err:
            raise ValidationError({"tap": _(f"{str(err)}")})
        return Response(
            {"payment_url": payment_url, "charge_id": charge_id},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_summary="List Wallet's transactions",
        operation_description="""
                list user's wallet transactions(debit,credit)
            """,
        tags=["Wallet",],
    )
    @action(
        methods=["GET"],
        detail=True,
        url_path="transactions",
        serializer_class=WalletTransactionSerializer,
    )
    def transactions(
        self, request: Request, *args: typing.Any, **kwargs: typing.Any
    ) -> Response:
        queryset = self.get_object().transactions.all().order_by("-created_at")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="List Wallet selection images",
        operation_description="""
                list wallet selection images
            """,
        tags=["Wallet",],
    )
    @action(
        methods=["GET",],
        detail=False,
        url_path="images",
        serializer_class=WalletMediaSerializer,
    )
    def images(
        self, request: Request, *args: typing.Any, **kwargs: typing.Any
    ) -> Response:
        queryset = WalletMedia.objects.filter(is_active=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class WalletV2ViewSet(
    mixins.ListModelMixin, viewsets.GenericViewSet,
):
    def get_queryset(self):
        return Wallet.objects.filter(
            user=self.request.user, is_active=True
        ).select_related("media_image")

    @swagger_auto_schema(
        operation_summary="List Wallet's transactions",
        operation_description="""
                list user's wallet transactions(debit,credit)
            """,
        tags=["Wallet",],
    )
    @action(
        methods=["GET"],
        detail=True,
        url_path="transactions",
        serializer_class=WalletTransactionListSerializer,
    )
    def transactions(self, request, *args, **kwargs):
        wallet = self.get_object()
        queryset = wallet.transactions.all().order_by("-created_at")
        serializer = WalletTransactionListSerializer(queryset, many=True)
        return Response({"results": serializer.data})


class PartnerAuthInfoViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = PartnerAuthInfo.objects.all()
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = PartnerAuthInfoSerializer
    filterset_class = PartnerAuthInfoFilter

    def get_object(self):
        return get_object_or_404(PartnerAuthInfo, user=self.request.user)

    @swagger_auto_schema(
        operation_summary="Send an OTP for PartnerAuthInfo",
        operation_description="""
                Send an OTP for PartnerAuthInfo
            """,
        tags=["Partner",],
    )
    @action(
        methods=["POST",],
        detail=False,
        url_path="send-otp",
        serializer_class=PartnerOTPRequestSerializer,
    )
    def send_otp(
        self, request: Request, *args: typing.Any, **kwargs: typing.Any
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"result": "ok"}, status=status.HTTP_201_CREATED, headers=headers
        )

    @swagger_auto_schema(
        operation_summary="verify Partner's Authentication ",
        operation_description="""
                verify Partner's Authentication for different auth methods
            """,
        tags=["Partner",],
    )
    @action(
        methods=["POST",],
        detail=False,
        url_path="",
        serializer_class=PartnerAuthInfoSerializer,
    )
    def verify(
        self, request: Request, *args: typing.Any, **kwargs: typing.Any
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @swagger_auto_schema(
        operation_summary="Retrieve User partner Auth",
        operation_description="""
                Retrieve User partner Auth
            """,
        tags=["Partner",],
    )
    def retrieve(
        self, request: Request, *args: typing.Any, **kwargs: typing.Any
    ) -> Response:
        return super().retrieve(request=request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete User partner Auth",
        operation_description="""
                Delete User partner Auth
            """,
        tags=["Partner",],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class PartnerViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet,
):
    queryset = Partner.objects.all()
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = PartnerSerializer
    filterset_class = PartnerFilter

    @swagger_auto_schema(
        operation_summary="Retrieve Partner",
        operation_description="""
                retireve a partner
            """,
        tags=["Partner",],
    )
    def retrieve(
        self, request: Request, *args: typing.Any, **kwargs: typing.Any
    ) -> Response:
        return super().retrieve(request=request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="List Partners",
        operation_description="""
                List  partners
            """,
        tags=["Partner",],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CountryPaymentMethodsViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = CountryPaymentMethod.objects.active()
    serializer_class = CountryPaymentMethodSerialzier
    filterset_class = CountryPaymentMethodFilter
    permission_classes = [
        permissions.AllowAny,
    ]

    @swagger_auto_schema(
        operation_summary="List Country Payment Methods",
        operation_description="""
                List Country Payment Methods
            """,
        tags=["Store",],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve Country Payment Method",
        operation_description="""
                Retrieve Country Payment Method
            """,
        tags=["Store",],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
