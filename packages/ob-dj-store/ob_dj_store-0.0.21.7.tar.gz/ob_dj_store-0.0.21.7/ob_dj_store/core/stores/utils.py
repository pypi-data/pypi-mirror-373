import math
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

import pycountry
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from config import settings


def get_data_dict(instance):
    """
    Get data dictionary from model instance.
    """
    return {
        field.name: getattr(instance, field.name)
        for field in instance._meta.fields
        if field.name not in ["id", "created_at", "updated_at"]
    }


def distance(origin, destination):
    """
    Calculate the Haversine distance.

    Parameters
    ----------
    origin : tuple of float
        (lat, long)
    destination : tuple of float
        (lat, long)

    Returns
    -------
    distance_in_km : float

    Examples
    --------
    >>> origin = (48.1372, 11.5756)  # Munich
    >>> destination = (52.5186, 13.4083)  # Berlin
    >>> round(distance(origin, destination), 1)
    504.2
    """
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(
        math.radians(lat1)
    ) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d


def get_currency_by_country(country_value):
    try:
        country = pycountry.countries.get(alpha_2=country_value)
        currency = pycountry.currencies.get(numeric=country.numeric)
        return currency.alpha_3
    except Exception as e:
        return None


def get_country_by_currency(currency):
    currency = pycountry.currencies.get(alpha_3=currency)
    country = pycountry.countries.get(numeric=currency.numeric)
    return country.alpha_2


def validate_currency(value):
    if not pycountry.currencies.get(alpha_3=value):
        raise ValidationError(
            _("%(value)s is not a currency"), params={"value": value},
        )


def round_up_tie(value, decimal_places=3):
    """Helper function to always round up when the 4th decimal is a 5"""
    decimal_value = Decimal(str(value))
    rounded_value = decimal_value.quantize(
        Decimal("1e-{0}".format(decimal_places)), rounding=ROUND_HALF_UP
    )
    return Decimal(rounded_value)


def get_arabic_fields(model, static_fields):
    all_fields = [field.name for field in model._meta.get_fields()]
    arabic_fields = {
        field.replace("_arabic", "")
        for field in all_fields
        if field.endswith("_arabic")
    }
    return list(set(static_fields) - set(arabic_fields))


class PartnerAuth:
    def __init__(self, email: str):
        from ob_dj_store.core.stores.models import PartnerAuthInfo, PartnerEmailDomain

        try:
            domain = PartnerEmailDomain.objects.get(email_domain=email.split("@")[1])
            self.partner = domain.partner
        except PartnerEmailDomain.DoesNotExist:
            raise ValidationError(_("Domain doesn't exist"))

        # verify email availability
        renew_time = now() + timedelta(
            hours=getattr(settings, "PARTNER_RENEW_AUTH_TIME", 24)
        )
        if PartnerAuthInfo.objects.filter(
            email=email, authentication_expires__gt=renew_time
        ).exists():
            raise ValidationError(_("This email is already in use"))
