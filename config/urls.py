
from django.contrib import admin
from django.urls import path, include
from generator import views

urlpatterns = [
    path("admin/", admin.site.urls),

    # Health
    path("api/health/", views.health),

    # Documents
    path("api/reports/", views.create_report),
    path(
        "api/reports/<uuid:report_id>/download/",
        views.download_report
    ),

    # OPay payments
    path("api/payments/create/", views.create_payment),
    path(
        "api/payments/<str:reference>/status/",
        views.payment_status
    ),
    path(
        "api/payments/<str:reference>/receipt/",
        views.upload_payment_receipt
    ),
    path(
        "api/payments/<str:reference>/review/",
        views.review_payment
    ),

    # Account
    path("api/account/", include("Account.urls")),
]


