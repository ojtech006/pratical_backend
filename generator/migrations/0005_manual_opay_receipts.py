from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("generator", "0004_subscription_packages")]

    operations = [
        migrations.AlterField(
            model_name="paymentorder", name="max_documents",
            field=models.PositiveSmallIntegerField(default=4),
        ),
        migrations.AlterField(
            model_name="paymentorder",
            name="plan",
            field=models.CharField(choices=[("FOUR_DOCS", "4 Documents")], default="FOUR_DOCS", max_length=20),
        ),
        migrations.AlterField(
            model_name="paymentorder",
            name="provider",
            field=models.CharField(default="OPAY", max_length=20),
        ),
        migrations.AlterField(
            model_name="paymentorder",
            name="status",
            field=models.CharField(
                choices=[("PENDING", "Awaiting receipt"), ("UNDER_REVIEW", "Under review"),
                         ("APPROVED", "Approved"), ("REJECTED", "Rejected")],
                default="PENDING", max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="paymentorder", name="receipt",
            field=models.FileField(blank=True, null=True, upload_to="payment_receipts/"),
        ),
        migrations.AddField(
            model_name="paymentorder", name="reviewed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="paymentorder", name="admin_note",
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
