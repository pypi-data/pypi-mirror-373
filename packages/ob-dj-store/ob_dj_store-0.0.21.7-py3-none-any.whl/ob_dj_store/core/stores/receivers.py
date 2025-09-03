from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from config import settings as store_settings
from ob_dj_store.core.stores.models import (
    Cart,
    Category,
    Order,
    OrderHistory,
    ProductMedia,
    ProductVariant,
    WalletMedia,
)
from ob_dj_store.utils.utils import resize_image


@receiver(
    post_save,
    sender=settings.AUTH_USER_MODEL,
    dispatch_uid="create_customer_cart_and_wallet_handler",
)
def create_customer_cart_and_wallet_handler(sender, instance, created, **kwargs):
    if not created:
        return
    cart = Cart(customer=instance)
    cart.save()
    wallet_media = WalletMedia.objects.filter(is_default=True)
    for currency in store_settings.WALLET_CURRENCIES:
        instance.wallets.create(currency=currency, media_image=wallet_media.first())


# add receiver to ProductVariant to create inventory


@receiver(
    post_save, sender=Order, dispatch_uid="create_order_history_handler",
)
def create_order_history_handler(sender, instance, created, **kwargs):
    try:
        OrderHistory.objects.create(
            order=instance, status=instance.status,
        )
    except Exception:
        pass


@receiver(
    pre_save, sender=Category, dispatch_uid="create_category_thumbnails",
)
def create_category_thumbnails(sender, instance, **kwargs):
    medium_dim = getattr(store_settings, "THUMBNAIL_MEDIUM_DIMENSIONS", None)
    small_dim = getattr(store_settings, "THUMBNAIL_SMALL_DIMENSIONS", None)
    if instance.image:
        if medium_dim:
            instance.image_thumbnail_medium = resize_image(
                instance.image,
                dim=medium_dim,
                size_name="medium",
                image_name=instance.name,
            )
        if small_dim:
            instance.image_thumbnail_small = resize_image(
                instance.image,
                dim=small_dim,
                size_name="small",
                image_name=instance.name,
            )


@receiver(
    pre_save, sender=ProductMedia, dispatch_uid="create_product_media_thumbnails",
)
def create_product_media_thumbnails(sender, instance, **kwargs):
    medium_dim = getattr(store_settings, "THUMBNAIL_MEDIUM_DIMENSIONS", None)
    small_dim = getattr(store_settings, "THUMBNAIL_SMALL_DIMENSIONS", None)
    if instance.image:
        if medium_dim:
            instance.image_thumbnail_medium = resize_image(
                instance.image,
                dim=medium_dim,
                size_name="medium",
                image_name=instance.name,
            )
        if small_dim:
            instance.image_thumbnail_small = resize_image(
                instance.image,
                dim=small_dim,
                size_name="small",
                image_name=instance.name,
            )


@receiver(
    pre_save, sender=WalletMedia, dispatch_uid="create_wallet_thumbnails",
)
def create_wallet_thumbnails(sender, instance, **kwargs):
    medium_dim = getattr(store_settings, "THUMBNAIL_MEDIUM_DIMENSIONS", None)
    if instance.image and medium_dim:
        instance.image_thumbnail_medium = resize_image(
            instance.image, dim=medium_dim, size_name="medium",
        )


@receiver(
    pre_save,
    sender=ProductVariant,
    dispatch_uid="create_product_vraiant_image_thumbnails",
)
def create_product_vraiant_image_thumbnails(sender, instance, **kwargs):
    medium_dim = getattr(store_settings, "THUMBNAIL_MEDIUM_DIMENSIONS", None)
    if instance.image and medium_dim:
        instance.image_thumbnail_medium = resize_image(
            instance.image, dim=medium_dim, size_name="medium",
        )
