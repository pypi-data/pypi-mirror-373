from rest_framework import serializers

from ob_dj_store.apis.stores.rest.serializers.serializers import OrderSerializer
from ob_dj_store.core.stores.gateway.tap.models import TapPayment


class TapPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TapPayment
        fields = [
            "id",
            "status",
            "payment",
            "result",
            "payment_url",
            "charge_id",
            "source",
            "amount",
            "init_response",
            "callback_response",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "status",
            "result",
            "payment_url",
            "init_response",
            "callback_response",
            "charge_id",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["orders"] = OrderSerializer(
            instance.payment.orders.all(), many=True
        ).data
        return representation
