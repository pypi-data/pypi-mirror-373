import logging

from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ob_dj_store.core.stores.gateway.stripe.models import StripePayment
from ob_dj_store.core.stores.gateway.stripe.utils import (
    handle_stripe_webhook,
    verify_webhook_signature,
)

from .serializers import (
    CreateStripePaymentSerializer,
    StripeCustomerSerializer,
    StripePaymentSerializer,
    StripePaymentStatusSerializer,
)

logger = logging.getLogger(__name__)


class StripePaymentViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Stripe payment management endpoints"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StripePaymentSerializer

    def get_queryset(self):
        """Filter stripe payments by current user"""
        return StripePayment.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == "create_payment":
            return CreateStripePaymentSerializer
        elif self.action == "check_status":
            return StripePaymentStatusSerializer
        return self.serializer_class

    @swagger_auto_schema(
        operation_summary="Create Stripe Payment",
        operation_description="""
            Create a Stripe PaymentIntent for an existing Payment object.
            Returns client_secret for frontend payment confirmation.
        """,
        tags=["Stripe Payment"],
        request_body=CreateStripePaymentSerializer,
        responses={
            201: openapi.Response(
                description="Payment intent created successfully",
                examples={
                    "application/json": {
                        "payment_intent_id": "pi_1234567890",
                        "client_secret": "pi_1234567890_secret_abc123",
                        "status": "requires_payment_method",
                        "amount": "25.00",
                        "currency": "usd",
                    }
                },
            )
        },
    )
    @action(detail=False, methods=["POST"])
    def create_payment(self, request):
        """Create a Stripe PaymentIntent for a payment"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = serializer.save()
        return Response(result, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Check Payment Status",
        operation_description="""
            Check the current status of a Stripe payment.
        """,
        tags=["Stripe Payment"],
        request_body=StripePaymentStatusSerializer,
    )
    @action(detail=False, methods=["POST"])
    def check_status(self, request):
        """Check the status of a Stripe payment"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment_intent_id = serializer.validated_data["payment_intent_id"]

        try:
            stripe_payment = StripePayment.objects.get(
                payment_intent_id=payment_intent_id, user=request.user
            )

            payment_serializer = StripePaymentSerializer(stripe_payment)
            return Response(payment_serializer.data)

        except StripePayment.DoesNotExist:
            return Response(
                {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        operation_summary="Get User's Stripe Customer",
        operation_description="""
            Get or create Stripe customer information for the current user.
        """,
        tags=["Stripe Payment"],
    )
    @action(detail=False, methods=["GET"])
    def customer(self, request):
        """Get user's Stripe customer information"""
        try:
            from ob_dj_store.core.stores.gateway.stripe.utils import (
                get_or_create_stripe_customer,
            )

            stripe_customer = get_or_create_stripe_customer(request.user)
            serializer = StripeCustomerSerializer(stripe_customer)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Error getting Stripe customer: {e}")
            return Response(
                {"error": "Failed to get customer information"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookViewSet(viewsets.GenericViewSet):
    """Stripe webhook endpoints"""

    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Stripe Webhook Callback",
        operation_description="""
            Handle Stripe webhook events for payment status updates.
            This endpoint is called by Stripe when payment events occur.
        """,
        tags=["Stripe Webhook"],
    )
    @action(detail=False, methods=["POST"])
    def callback(self, request):
        """Handle Stripe webhook callbacks"""
        logger.info(
            f"Received webhook request from IP: {request.META.get('REMOTE_ADDR')}"
        )
        logger.info(f"Request headers: {dict(request.META)}")

        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        logger.info(f"Payload length: {len(payload)}")
        logger.info(f"Signature header present: {bool(sig_header)}")

        if not sig_header:
            logger.warning("Missing Stripe signature header")
            return HttpResponseBadRequest("Missing signature")

        try:
            # Verify webhook signature
            event = verify_webhook_signature(payload, sig_header)
            logger.info(f"Received Stripe webhook: {event['type']}")

            # Handle the webhook
            result = handle_stripe_webhook(event)

            if result:
                logger.info("Webhook processed successfully")
                return HttpResponse("OK", status=200)
            else:
                logger.error("Failed to process webhook")
                return HttpResponseBadRequest("Failed to process webhook")

        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            return HttpResponseBadRequest("Invalid payload")
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            import traceback

            logger.error(f"Webhook error traceback: {traceback.format_exc()}")
            return HttpResponseBadRequest(str(e))
