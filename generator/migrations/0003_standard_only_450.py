from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("generator", "0002_standard_vip_ai"),
    ]

    operations = [
        migrations.AlterField(
            model_name="paymentorder",
            name="plan",
            field=models.CharField(
                choices=[("STANDARD", "Standard")],
                default="STANDARD",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="paymentorder",
            name="amount_kobo",
            field=models.PositiveIntegerField(default=45000),
        ),
        migrations.AlterField(
            model_name="practicalreport",
            name="plan",
            field=models.CharField(
                choices=[("STANDARD", "Standard")],
                default="STANDARD",
                max_length=20,
            ),
        ),
    ]
