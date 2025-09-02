import json
import logging
from asyncio.log import logger

import requests
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from config import settings
from ob_dj_store.core.stores.models import Payment

User = get_user_model()
logger = logging.getLogger(__name__)


class TapException(Exception):
    pass


def get_tap_headers():
    tap_secret_key = settings.TAP_SECRET_KEY
    headers = {
        "authorization": f"Bearer {tap_secret_key}",
        "content-type": "application/json",
        "cache-control": "no-cache",
    }
    return headers


def retrieve_customer_id(customer):
    from ob_dj_store.core.stores.gateway.tap.models import TapCustomer

    # contact Tap api
    try:
        tap_customer = TapCustomer.objects.get(customer=customer)
        return tap_customer
    except ObjectDoesNotExist:
        pass

    payload = {
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "email": customer.email,
    }
    phone_number = getattr(customer, "phone_number", None)
    if phone_number:
        payload["phone"] = {
            "country_code": str(phone_number.country_code),
            "number": str(phone_number.national_number),
        }
    response = requests.post(
        f"{settings.TAP_API_URL}/customers",
        headers=get_tap_headers(),
        data=json.dumps(payload, cls=DjangoJSONEncoder),
    )
    if response.status_code == 200:
        response_dict = response.json()
        tap_customer = TapCustomer.objects.create(
            customer=customer,
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
            phone_number=phone_number,
            tap_customer_id=response_dict["id"],
            init_data=response_dict,
        )
        return tap_customer
    else:
        logger.error(f"Error accured while creating tap customer:{response.text}")
        print(f"Error accured while creating tap customer:{response.text}")
        raise TapException(_("Error accured while creating tap customer"))


def initiate_payment(
    source: str, user: User, payment: Payment, currency_code: str,
):
    """Initiate payment URL and return charge_id, payment_url and response"""

    redirect_path = reverse(f"tap_gateway:taptransaction-get")
    callback_path = reverse(f"tap_gateway:taptransaction-callback")
    redirect_url = f"{settings.WEBSITE_URI}{redirect_path}"
    callback_url = f"{settings.WEBSITE_URI}{callback_path}"

    order = payment.orders.all().first()
    extra_infos = order.extra_infos
    display_source = None
    if source in [
        settings.APPLE_PAY,
        settings.GOOGLE_PAY,
    ]:
        token_data = extra_infos.get("tap_token")
        if not token_data:
            raise ValidationError(
                _(f"Order(PK={order.pk}) does not have tap_token for {source} payment")
            )
        display_source = source
        source = token_data["id"]
    tap_customer = retrieve_customer_id(user)
    payload = {
        "amount": "%.3f" % payment.total_payment,
        "currency": currency_code,
        "source": {"id": source},
        "customer": {"id": tap_customer.tap_customer_id,},
        "post": {"url": callback_url},
        "redirect": {"url": redirect_url},
    }

    url = "/charges/"
    method = "POST"
    if not settings.TAP_SECRET_KEY:
        raise ValueError("TAP Secret is missing from settings")

    payload = json.dumps(payload, cls=DjangoJSONEncoder)
    response = requests.request(
        url=f"{settings.TAP_API_URL}{url}",
        method=method,
        data=payload,
        headers=get_tap_headers(),
    )
    tap_response = response.json()
    logger.info(f"tap payment initiated!")
    payment_transaction = tap_response.get("transaction", None)
    charge_id = tap_response.get("id")
    tap_sources = [
        settings.TAP_CREDIT_CARD,
        settings.TAP_KNET,
        settings.TAP_ALL,
        settings.MADA,
        settings.BENEFIT,
    ]
    if not payment_transaction and source in tap_sources:
        # TODO: How does this issue occur and is this the best way to handle it?
        logger.error(f"Failed to return payment_url  : {response.text}")
        raise TapException("Failed to create charge request no payment_url returned.")
    if not charge_id:
        logger.error(f"tap charge request payload:{payload}")
        logger.error(f"order extra infos:{extra_infos}")
        logger.error(f"Failed to return charge_id : {response.text}")
        raise TapException("Failed to return charge_id")
    payment_url = payment_transaction.get("url")
    status = tap_response.get("status")
    source = tap_response.get("source").get("id") if source else ""
    if status == "CAPTURED":
        payment.mark_paid()

    return {
        "charge_id": charge_id,
        "payment_url": payment_url,
        "init_response": tap_response,
        "source": display_source if display_source else source,
        "status": status,
    }
