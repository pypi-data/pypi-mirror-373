import logging
import typing

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from ob_dj_store.apis.tap.serializers import TapPaymentSerializer
from ob_dj_store.core.stores.gateway.tap.models import TapPayment

logger = logging.getLogger(__name__)


class TapPaymentViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    http_method_names = ["get", "post"]
    queryset = TapPayment.objects.all()
    serializer_class = TapPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="gateway_tap callback",
        operation_description="""
            gateway_tap callback
        """,
        tags=["TAP Payment",],
    )
    @action(detail=False, methods=["POST"], permission_classes=[permissions.AllowAny])
    def callback(self, request) -> typing.Any:
        tap_payload = request.data
        charge_id = tap_payload.get("id", None)
        if not charge_id:
            raise ValidationError(_("charge_id attribute is required"))
        try:
            logger.info(f"Received callback with payload {tap_payload}")
            instance = TapPayment.objects.get(charge_id=charge_id)
            instance.callback_update(tap_payload)
        except ObjectDoesNotExist:
            logger.info(
                f"Callback received from TAP with ID: {charge_id.__str__()} not found"
            )
            return HttpResponseNotFound("Wrong charge Id")

        return Response({"success": True}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Retrieve TAP Transaction",
        operation_description="""
            Retrieve Tap Transaction from charge id
        """,
        tags=["TAP Payment",],
    )
    @action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
    def get(self, request, *args, **kwargs):
        charge_id = request.query_params.get("tap_id", None)
        if not charge_id:
            raise ValidationError(_("tap_id required in params."))
        instance = get_object_or_404(TapPayment, charge_id=charge_id)

        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
