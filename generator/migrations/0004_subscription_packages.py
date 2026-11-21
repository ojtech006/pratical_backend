from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("generator", "0003_standard_only_450"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentorder",
            name="max_documents",
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="paymentorder",
            name="plan",
            field=models.CharField(
                choices=[("FOUR_DOCS", "4 Documents"), ("SIX_DOCS", "6 Documents"), ("STANDARD", "Legacy Standard")],
                default="FOUR_DOCS",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="practicalreport",
            name="plan",
            field=models.CharField(
                choices=[("FOUR_DOCS", "4 Documents"), ("SIX_DOCS", "6 Documents"), ("STANDARD", "Legacy Standard")],
                default="STANDARD",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="practicalreport",
            name="payment_order",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="reports",
                to="generator.paymentorder",
            ),
        ),
    ]
