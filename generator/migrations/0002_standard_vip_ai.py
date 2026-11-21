from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [("generator", "0001_initial")]
    operations = [
        migrations.AddField(model_name="paymentorder", name="plan", field=models.CharField(choices=[("STANDARD", "Standard"), ("VIP_AI", "VIP AI")], default="STANDARD", max_length=20)),
        migrations.AddField(model_name="practicalreport", name="assignment_type", field=models.CharField(choices=[("SUMMARY", "Practical Class Summary"), ("EXERCISES", "Practical Exercises")], default="SUMMARY", max_length=20)),
        migrations.AddField(model_name="practicalreport", name="plan", field=models.CharField(choices=[("STANDARD", "Standard"), ("VIP_AI", "VIP AI")], default="STANDARD", max_length=20)),
        migrations.AddField(model_name="practicalreport", name="course_title", field=models.CharField(blank=True, max_length=160)),
        migrations.AddField(model_name="practicalreport", name="lecturer", field=models.CharField(blank=True, max_length=160)),
        migrations.AddField(model_name="practicalreport", name="application_letter", field=models.TextField(blank=True)),
        migrations.AddField(model_name="practicalreport", name="cv_content", field=models.TextField(blank=True)),
        migrations.AddField(model_name="practicalreport", name="saving_steps", field=models.TextField(blank=True)),
        migrations.AddField(model_name="practicalreport", name="extra_notes", field=models.TextField(blank=True)),
        migrations.AddField(model_name="practicalreport", name="ai_generated", field=models.BooleanField(default=False)),
        migrations.AlterField(model_name="practicalreport", name="summary", field=models.TextField(blank=True)),
        migrations.AddField(model_name="practicalreport", name="payment_order", field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="report", to="generator.paymentorder")),
        migrations.CreateModel(name="DailyDownload", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("download_date", models.DateField()), ("count", models.PositiveSmallIntegerField(default=0)), ("report", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="daily_downloads", to="generator.practicalreport"))], options={"constraints": [models.UniqueConstraint(fields=("report", "download_date"), name="unique_report_download_day")]}),
    ]
