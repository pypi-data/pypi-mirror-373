from django.conf.urls import include
from django.urls import path
from rest_framework_nested import routers

from ob_dj_store.apis.stores.views import (
    CartItemView,
    CartView,
    CategoryViewSet,
    CountryPaymentMethodsViewSet,
    FavoriteViewSet,
    InventoryView,
    OrderView,
    PartnerAuthInfoViewSet,
    PartnerViewSet,
    PaymentMethodViewSet,
    ProductView,
    ReorderViewSet,
    ShippingMethodViewSet,
    StoreView,
    TaxViewSet,
    TransactionsViewSet,
    VariantView,
    WalletV2ViewSet,
    WalletViewSet,
)

app_name = "stores"

router = routers.SimpleRouter()
router.register(r"stores", StoreView)

stores_router = routers.NestedSimpleRouter(router, r"stores", lookup="store")
stores_router.register(r"order", OrderView, basename="order")
stores_router.register(r"product", ProductView, basename="product")
stores_router.register(r"variant", VariantView, basename="variant")
stores_router.register(r"inventory", InventoryView, basename="inventory")
stores_router.register(
    r"shipping-method", ShippingMethodViewSet, basename="shipping-method"
)
router.register(r"tax", TaxViewSet, basename="tax")
router.register(r"category", CategoryViewSet, basename="category")
router.register(r"transaction", TransactionsViewSet, basename="transaction")
router.register(r"cart", CartView, basename="cart")
router.register(r"cart-item", CartItemView, basename="cart-item")
router.register(r"favorite", FavoriteViewSet, basename="favorite")
router.register(r"wallet", WalletViewSet, basename="wallet")
router.register(r"wallet_v2", WalletV2ViewSet, basename="wallet_v2")
router.register(r"payment-method", PaymentMethodViewSet, basename="payment-method")
router.register(r"order", ReorderViewSet, basename="re-order")
router.register(r"partner/auth", PartnerAuthInfoViewSet, basename="auth")
router.register(r"partner", PartnerViewSet, basename="partner")
router.register(
    r"payment-method/country",
    CountryPaymentMethodsViewSet,
    basename="country-payment-methods",
)

urlpatterns = [
    path(r"", include(router.urls)),
    path(r"", include(stores_router.urls)),
]
