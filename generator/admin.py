from django.contrib import admin, messages
from django.utils import timezone
from .models import PracticalReport, PaymentOrder, DailyDownload


@admin.action(description="Approve selected verified OPay payments")
def approve_opay_payments(modeladmin, request, queryset):
    updated = 0
    for order in queryset.select_for_update():
        if order.status == "UNDER_REVIEW" and order.receipt:
            order.status = "APPROVED"
            order.reviewed_at = timezone.now()
            order.admin_note = "Approved after checking the OPay transaction."
            order.save(update_fields=["status", "reviewed_at", "admin_note"])
            updated += 1
    modeladmin.message_user(request, f"{updated} payment(s) approved. Four credits are active for each.", messages.SUCCESS)


@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    list_display = ("reference", "plan", "amount_kobo", "status", "provider", "created_at", "reviewed_at")
    list_filter = ("status", "provider", "created_at")
    search_fields = ("reference",)
    readonly_fields = ("reference", "created_at", "reviewed_at")
    actions = [approve_opay_payments]


admin.site.register(PracticalReport)
admin.site.register(DailyDownload)
