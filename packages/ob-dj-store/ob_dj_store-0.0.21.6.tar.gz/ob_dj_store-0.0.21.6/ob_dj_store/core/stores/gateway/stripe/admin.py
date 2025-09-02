"""
Stripe Payment Gateway Admin

This module contains the admin configuration for Stripe payment models.
"""

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from ob_dj_store.core.stores.gateway.stripe.models import StripeCustomer, StripePayment


@admin.register(StripePayment)
class StripePaymentAdmin(ImportExportModelAdmin):
    list_display = (
        "payment_intent_id",
        "payment",
        "user",
        "status",
        "amount",
        "currency",
        "source",
        "created_at",
    )
    list_filter = ("status", "source", "created_at")
    search_fields = ("payment_intent_id", "user__email", "payment__id")
    readonly_fields = (
        "payment_intent_id",
        "client_secret",
        "init_response",
        "webhook_response",
        "created_at",
        "updated_at",
    )
    raw_id_fields = ("payment", "user")
    date_hierarchy = "created_at"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("payment__payment_tax", "user")
            .prefetch_related(
                "payment__orders__items", "payment__orders__shipping_method"
            )
        )

    def amount(self, obj):
        """Display payment amount"""
        return f"${obj.amount:.2f}"

    amount.short_description = "Amount"

    def currency(self, obj):
        """Display payment currency"""
        return obj.currency.upper()

    currency.short_description = "Currency"


@admin.register(StripeCustomer)
class StripeCustomerAdmin(ImportExportModelAdmin):
    list_display = (
        "stripe_customer_id",
        "email",
        "first_name",
        "last_name",
        "customer",
        "created_at",
    )
    search_fields = ("stripe_customer_id", "email", "first_name", "last_name")
    readonly_fields = ("stripe_customer_id", "init_data", "created_at", "updated_at")
    raw_id_fields = ("customer",)
    date_hierarchy = "created_at"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("customer")
