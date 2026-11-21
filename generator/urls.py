from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health, name="generator-health"),
    path("payments/create/", views.create_payment, name="create-payment"),
    path("payments/<str:reference>/receipt/", views.upload_payment_receipt, name="upload-payment-receipt"),
    path("payments/<str:reference>/status/", views.payment_status, name="payment-status"),
    path("payments/<str:reference>/review/", views.review_payment, name="review-payment"),
    path("reports/", views.create_report, name="create-report"),
    path("reports/<uuid:report_id>/download/", views.download_report, name="download-report"),
]
