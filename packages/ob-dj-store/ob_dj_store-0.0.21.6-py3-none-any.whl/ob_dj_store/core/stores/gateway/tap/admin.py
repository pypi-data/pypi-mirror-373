from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from ob_dj_store.core.stores.gateway.tap.models import TapCustomer, TapPayment


class TapPaymentAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = [
        "charge_id",
        "amount",
        "source",
        "currency",
        "status",
        "updated_at",
        "created_at",
    ]
    list_filter = ("status", "source")
    search_fields = [
        "charge_id",
    ]
    date_hierarchy = "created_at"

    def get_queryset(self, request):

        return (
            super()
            .get_queryset(request)
            .select_related("payment__payment_tax",)
            .prefetch_related(
                "payment__orders__items", "payment__orders__shipping_method"
            )
        )


class TapCustomerAdmin(admin.ModelAdmin):
    list_display = [
        "customer_id",
        "customer",
        "email",
        "phone_number",
        "created_at",
    ]
    search_fields = [
        "customer__email",
    ]


admin.site.register(TapPayment, TapPaymentAdmin)
admin.site.register(TapCustomer, TapCustomerAdmin)
