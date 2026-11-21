from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("generator", "0006_single_450_plan"),
    ]

    operations = [
        migrations.AddField(
            model_name="practicalreport",
            name="exercise_template",
            field=models.CharField(
                choices=[
                    ("CLASSIC_SAMPLE", "Classic Student Template"),
                    ("SIMPLE_SAMPLE", "Simple COS 101 Template"),
                ],
                default="CLASSIC_SAMPLE",
                max_length=24,
            ),
        ),
    ]
