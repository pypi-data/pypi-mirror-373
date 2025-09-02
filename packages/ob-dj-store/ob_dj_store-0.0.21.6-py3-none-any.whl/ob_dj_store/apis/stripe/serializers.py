from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from ob_dj_store.core.stores.gateway.stripe.models import StripeCustomer, StripePayment
from ob_dj_store.core.stores.gateway.stripe.utils import StripeException
from ob_dj_store.core.stores.models import Payment, PaymentMethod

User = get_user_model()


class StripeCustomerSerializer(serializers.ModelSerializer):
    """Serializer for Stripe customer information"""

    class Meta:
        model = StripeCustomer
        fields = [
            "stripe_customer_id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "created_at",
        ]
        read_only_fields = ["stripe_customer_id", "created_at"]


class StripePaymentSerializer(serializers.ModelSerializer):
    """Serializer for Stripe payment information"""

    amount = serializers.DecimalField(max_digits=10, decimal_places=3, read_only=True)
    currency = serializers.CharField(read_only=True)
    payment_url = serializers.CharField(read_only=True)

    class Meta:
        model = StripePayment
        fields = [
            "payment_intent_id",
            "client_secret",
            "status",
            "source",
            "amount",
            "currency",
            "payment_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "payment_intent_id",
            "client_secret",
            "status",
            "source",
            "amount",
            "currency",
            "payment_url",
            "created_at",
            "updated_at",
        ]


class CreateStripePaymentSerializer(serializers.Serializer):
    """Serializer for creating Stripe payments"""

    payment_id = serializers.IntegerField(
        help_text="ID of the Payment object to process with Stripe"
    )
    return_url = serializers.URLField(
        required=False,
        help_text="URL to redirect to after payment completion (optional)",
    )

    def validate_payment_id(self, value):
        """Validate that the payment exists and belongs to the user"""
        user = self.context["request"].user

        try:
            payment = Payment.objects.get(id=value, user=user)
        except Payment.DoesNotExist:
            raise serializers.ValidationError(
                _("Payment not found or does not belong to you.")
            )

        # Check if payment method is Stripe
        if payment.method.payment_provider != "stripe":
            raise serializers.ValidationError(_("Payment method must be Stripe."))

        # Check if payment is already processed
        if hasattr(payment, "stripe_payment"):
            if payment.stripe_payment.status in ["succeeded", "canceled"]:
                raise serializers.ValidationError(
                    _("Payment has already been processed.")
                )

        return value

    def create(self, validated_data):
        """Create a Stripe PaymentIntent for the payment"""
        user = self.context["request"].user
        payment_id = validated_data["payment_id"]
        return_url = validated_data.get("return_url")

        payment = Payment.objects.get(id=payment_id, user=user)

        try:
            # Create or get existing Stripe payment
            if hasattr(payment, "stripe_payment"):
                stripe_payment = payment.stripe_payment
            else:
                stripe_payment = StripePayment.objects.create(
                    payment=payment, user=user
                )

            return {
                "payment_intent_id": stripe_payment.payment_intent_id,
                "client_secret": stripe_payment.client_secret,
                "status": stripe_payment.status,
                "amount": stripe_payment.amount,
                "currency": stripe_payment.currency,
                "return_url": return_url,
            }

        except StripeException as e:
            raise serializers.ValidationError({"stripe": str(e)})


class StripePaymentStatusSerializer(serializers.Serializer):
    """Serializer for checking Stripe payment status"""

    payment_intent_id = serializers.CharField(
        help_text="Stripe PaymentIntent ID to check status for"
    )

    def validate_payment_intent_id(self, value):
        """Validate that the payment intent exists and belongs to the user"""
        user = self.context["request"].user

        try:
            stripe_payment = StripePayment.objects.get(
                payment_intent_id=value, user=user
            )
        except StripePayment.DoesNotExist:
            raise serializers.ValidationError(
                _("Payment intent not found or does not belong to you.")
            )

        return value


class StripeWebhookEventSerializer(serializers.Serializer):
    """Serializer for processing Stripe webhook events"""

    id = serializers.CharField()
    type = serializers.CharField()
    data = serializers.DictField()

    def validate(self, attrs):
        """Validate webhook event structure"""
        if "object" not in attrs.get("data", {}):
            raise serializers.ValidationError(_("Invalid webhook event structure."))

        return attrs


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for payment methods with Stripe support"""

    supports_stripe = serializers.SerializerMethodField()

    class Meta:
        model = PaymentMethod
        fields = [
            "id",
            "name",
            "name_arabic",
            "description",
            "description_arabic",
            "payment_provider",
            "is_active",
            "supports_stripe",
        ]
        read_only_fields = ["supports_stripe"]

    def get_supports_stripe(self, obj):
        """Check if this payment method supports Stripe"""
        return obj.payment_provider == "stripe"
