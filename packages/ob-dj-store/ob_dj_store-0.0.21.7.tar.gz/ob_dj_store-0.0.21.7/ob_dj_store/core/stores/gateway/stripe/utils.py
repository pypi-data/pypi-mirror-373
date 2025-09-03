"""
Stripe Payment Gateway Utilities

This module contains utility functions for Stripe payment integration.
"""

import logging

import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, ValidationError

User = get_user_model()
logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


class StripeException(Exception):
    """Custom exception for Stripe-related errors"""


def get_or_create_stripe_customer(user):
    """Get or create a Stripe customer for the user"""
    from ob_dj_store.core.stores.gateway.stripe.models import StripeCustomer

    try:
        return StripeCustomer.objects.get(customer=user)
    except ObjectDoesNotExist:
        pass

    # Create customer in Stripe
    try:
        customer_data = {
            "name": f"{user.first_name} {user.last_name}".strip(),
            "email": user.email,
            "metadata": {"user_id": str(user.id), "platform": "ob-dj-store"},
        }

        # Add phone if available
        phone_number = getattr(user, "phone_number", None)
        if phone_number:
            customer_data["phone"] = str(phone_number)

        stripe_customer = stripe.Customer.create(**customer_data)

        # Save to database
        customer_record = StripeCustomer.objects.create(
            customer=user,
            stripe_customer_id=stripe_customer.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone_number=phone_number,
            init_data=stripe_customer,
        )

        logger.info(f"Created Stripe customer {stripe_customer.id} for user {user.id}")
        return customer_record

    except stripe.error.StripeError as e:
        logger.error(f"Failed to create Stripe customer: {str(e)}")
        raise StripeException(f"Failed to create customer: {str(e)}")


def initiate_stripe_payment(user, payment, currency_code):
    """Initiate a Stripe PaymentIntent"""

    try:
        # Get or create Stripe customer
        stripe_customer = get_or_create_stripe_customer(user)

        # Get the first order for metadata
        order = payment.orders.first()

        # Prepare PaymentIntent data
        intent_data = {
            "amount": int(payment.total_payment * 100),  # Convert to cents
            "currency": currency_code.lower(),
            "customer": stripe_customer.stripe_customer_id,
            "metadata": {
                "payment_id": str(payment.id),
                "user_id": str(user.id),
                "order_id": str(order.id) if order else None,
                "platform": "ob-dj-store",
            },
            "automatic_payment_methods": {"enabled": True,},
        }

        # Add description
        if order:
            intent_data[
                "description"
            ] = f"Order #{order.id} from {order.store.name if order.store else 'Store'}"

        # Create PaymentIntent
        payment_intent = stripe.PaymentIntent.create(**intent_data)

        logger.info(
            f"Created Stripe PaymentIntent {payment_intent.id} for payment {payment.id}"
        )

        return {
            "payment_intent_id": payment_intent.id,
            "client_secret": payment_intent.client_secret,
            "status": payment_intent.status,
            "init_response": payment_intent,
        }

    except stripe.error.StripeError as e:
        logger.error(f"Failed to create PaymentIntent: {str(e)}")
        raise StripeException(f"Failed to initiate payment: {str(e)}")


def handle_stripe_webhook(event_data):
    """Handle Stripe webhook events"""
    from ob_dj_store.core.stores.gateway.stripe.models import StripePayment

    event_type = event_data.get("type")

    # List of payment_intent events we handle
    payment_intent_events = [
        "payment_intent.succeeded",
        "payment_intent.payment_failed",
        "payment_intent.canceled",
        "payment_intent.requires_action",
        "payment_intent.processing",
    ]

    if event_type in payment_intent_events:
        payment_intent = event_data["data"]["object"]
        payment_intent_id = payment_intent["id"]

        try:
            stripe_payment = StripePayment.objects.get(
                payment_intent_id=payment_intent_id
            )
            stripe_payment.webhook_update(event_data)
            logger.info(
                f"Successfully processed {event_type} for PaymentIntent {payment_intent_id}"
            )
            return True
        except ObjectDoesNotExist:
            logger.warning(
                f"Received webhook for unknown PaymentIntent: {payment_intent_id}"
            )
            # Return True for unknown payments to acknowledge webhook (don't retry)
            return True

    # Log unhandled events but return True (acknowledged)
    logger.info(f"Unhandled Stripe webhook event: {event_type}")
    return True


def verify_webhook_signature(payload, signature):
    """Verify Stripe webhook signature and return event data"""
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, settings.STRIPE_WEBHOOK_SECRET
        )
        return event
    except ValueError:
        logger.error("Invalid webhook payload")
        raise ValidationError("Invalid payload")
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid webhook signature")
        raise ValidationError("Invalid signature")
