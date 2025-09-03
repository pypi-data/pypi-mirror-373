import logging
from datetime import timedelta

from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from ob_dj_otp.core.otp.models import OneTruePairing

from ob_dj_store.core.stores.managers import PartnerAuthInfoManager
from ob_dj_store.core.stores.models._store import Store
from ob_dj_store.utils.model import DjangoModelCleanMixin

logger = logging.getLogger(__name__)


class Discount(models.Model):
    discount_pos_id = models.CharField(max_length=200, null=True, blank=True)
    discount_rate = models.DecimalField(
        max_digits=6, decimal_places=3, validators=[MaxValueValidator(limit_value=1)]
    )
    is_active = models.BooleanField(default=True)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.discount_rate * 100}% Discount"

    def perc_to_flat(self, amount):
        return amount * self.discount_rate


def default_offer_end_time():
    return now() + timedelta(days=getattr(settings, "DEFAULT_PARTNER_OFFER_TIME", 60))


class Partner(DjangoModelCleanMixin, models.Model):
    class AuthMethods(models.TextChoices):
        OTP = "OTP", _("One True Pairing")
        CODE = "CODE", _("Promotion code")

    name = models.CharField(_("Partner's Name"), max_length=255)
    name_arabic = models.CharField(null=True, blank=True, max_length=255)
    stores = models.ManyToManyField(Store, related_name="partners")
    promotion_code = models.PositiveBigIntegerField(
        _("Promotion code"), null=True, blank=True, unique=True
    )
    auth_method = models.CharField(
        _("Authentication method"), max_length=255, choices=AuthMethods.choices
    )
    country = CountryField(help_text=_("Partner's country."))
    discount = models.ForeignKey(
        Discount, on_delete=models.PROTECT, related_name="partners"
    )
    offer_start_time = models.DateTimeField(_("Offer start date"), default=now)
    offer_end_time = models.DateTimeField(
        _("Offer end date"), default=default_offer_end_time
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name}"


class PartnerEmailDomain(DjangoModelCleanMixin, models.Model):
    partner = models.ForeignKey(
        Partner, on_delete=models.CASCADE, related_name="domains"
    )
    email_domain = models.CharField(max_length=255, unique=True)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PartnerAuthInfo(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", _("Active")
        INACTIVE = "INACTIVE", _("Inactive")
        EXPIRED = "EXPIRED", _("Expired")

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.EmailField(_("Partner's Email"))
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    authentication_details = models.JSONField(null=True, blank=True)
    authentication_expires = models.DateTimeField()
    status = models.CharField(
        _("Status of User's Authentication"),
        max_length=100,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(_("Last Authentifacation"), auto_now=True)

    objects = PartnerAuthInfoManager()

    def save(self, **kwargs) -> None:
        expiration_date = now() + timedelta(
            days=getattr(settings, "PARTNER_AUTH_TIME", 365)
        )
        if self.partner.offer_end_time < expiration_date:
            self.authentication_expires = self.partner.offer_end_time
        else:
            self.authentication_expires = expiration_date
        return super().save(**kwargs)


class PartnerOTPAuth(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.OneToOneField(
        OneTruePairing, on_delete=models.PROTECT, related_name="partner_otp_auth"
    )
    partner = models.ForeignKey(
        Partner, on_delete=models.CASCADE, related_name="otp_auths"
    )
    email = models.EmailField(_("Partner's Email"))

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"PartnerOTPAuth(PK={self.pk})"
