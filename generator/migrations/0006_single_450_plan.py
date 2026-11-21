from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("generator", "0005_manual_opay_receipts")]

    operations = [
        migrations.AlterField(
            model_name="practicalreport",
            name="plan",
            field=models.CharField(
                choices=[("FOUR_DOCS", "4 Documents")],
                default="STANDARD",
                max_length=20,
            ),
        ),
    ]
