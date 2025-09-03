from django.apps import apps
from django.core.checks import Error
from django.utils.module_loading import import_string

from config import settings

REQUIRED_INSTALLED_APPS = [
    "rest_framework",
]


def required_installed_apps(app_configs, **kwargs):
    return [
        Error(f"{app} is required in INSTALLED_APPS")
        for app in REQUIRED_INSTALLED_APPS
        if not apps.is_installed(app)
    ]


class Payment:
    pass


def store_validation_settings(app_configs, **kwargs):
    errors = []
    path = getattr(settings, "GIFT_PAYMENT_METHOD_PATH", None)
    if getattr(settings, "GIFT", None) and not path:
        errors.append(
            Error(
                "GIFT_PAYMENT_METHOD_PATH must be set if GIFT is in Payment methods",
                id="store_validation_settings_error",
            )
        )
    else:
        try:
            gift_payment_function = import_string(path)
            result = gift_payment_function(Payment(), 32)
            if not (result.get("success", None) and result.get("error", "") != ""):
                errors.append(
                    Error(
                        f"the gift payment function should return a dict with 2 keys 'success' and 'error' : {result}"
                    )
                )
        except ImportError:
            errors.append(
                Error(
                    f"{path} is not a valid path", id="store_validation_settings_error"
                )
            )
        except TypeError:
            errors.append(
                Error(
                    f"{gift_payment_function} should have 2 arguements payment:Payment, gift_card_id:int"
                )
            )

    def _path_validation(path):
        try:
            path_class = import_string(path)
        except ImportError:
            errors.append(
                Error(
                    f"{path} is not a valid path", id="store_validation_settings_error"
                )
            )

    if hasattr(settings, "GIFT_PAYMENT_METHOD_PATH"):
        _path_validation(settings.GIFT_PAYMENT_METHOD_PATH)

    # Favorite validation settings
    if hasattr(settings, "FAVORITE_TYPES"):
        for key, favorite in settings.FAVORITE_TYPES.items():
            if not favorite.get("path"):
                errors.append(
                    Error(
                        f"Model path should be set for {key}",
                        id="store_validation_settings_error",
                    )
                )
            else:
                _path_validation(favorite["path"])
            if favorite.get("extras", None):
                for key_extra, extra in favorite["extras"].items():
                    if not extra.get("path", None):
                        errors.append(
                            Error(
                                f"Model path should be set for {key}",
                                id="store_validation_settings_error",
                            )
                        )
                    else:
                        _path_validation(extra["path"])
                    if extra.get("type", None) == None:
                        errors.append(
                            Error(
                                f"type must be set for {key_extra}",
                                id="store_validation_settings_error",
                            )
                        )
                    else:
                        if not (
                            hasattr(settings, "SIGNLE_FAVORITE_EXTRA")
                            and hasattr(settings, "MULTIPLE_FAVORITE_EXTRA")
                        ):
                            errors.append(
                                Error(
                                    f"SIGNLE_FAVORITE_EXTRA and MULTIPLE_FAVORITE_EXTRA must be set",
                                    id="store_validation_settings_error",
                                )
                            )

    return errors
