from datetime import time, timedelta
from email.utils import localtime
from importlib import import_module

from django.conf import settings
from django.utils.timezone import now


class EmptyCalss:
    pass


def import_class_from_string(serializer_class_name):
    mixin_path = settings.SERIALIZERS_MIXIN.get(serializer_class_name)
    if not mixin_path:
        return EmptyCalss
    module_path, class_name = mixin_path.rsplit(".", 1)
    module = import_module(module_path)
    return getattr(module, class_name)


def product_media_upload_to(instance, filename):
    ext = filename.split(".")[-1]
    return f"product_media/{instance.product.name}_{instance.order_value}_{int(now().timestamp())}.{ext}"


def product_variant_media_upload_to(instance, filename):
    ext = filename.split(".")[-1]
    return f"product_variant_media/{instance.product.name}_{instance.name}_{int(now().timestamp())}.{ext}"


def category_media_upload_to(instance, filename):
    ext = filename.split(".")[-1]
    if instance:
        return f"category_media/{instance.name}_{instance.order_value}_{int(now().timestamp())}.{ext}"


def store_media_upload_to(instance, filename):
    ext = filename.split(".")[-1]
    if instance:
        return f"store_media/{instance.name}_{int(now().timestamp())}.{ext}"


def wallet_media_upload_to(instance, filename):
    image_name, ext = filename.split(".")
    if instance:
        return f"wallets/{image_name}_{int(now().timestamp())}.{ext}"


def import_gift_payment_function(function_path):
    module_path, class_name = function_path.rsplit(".", 1)
    module = import_module(module_path)
    Mixin = getattr(module, class_name)
    return Mixin


def get_from_and_to_hours():
    current_time = localtime(now())
    from_hour = (current_time - timedelta(hours=1)).time()
    to_hour = (current_time + timedelta(hours=1)).time()

    if to_hour < current_time.time():
        to_hour = time(23, 59)
    if from_hour > current_time.time():
        from_hour = time(0, 0)
    return {"from_hour": from_hour, "to_hour": to_hour}
