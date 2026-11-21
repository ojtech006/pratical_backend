# Generated initial migration for PracticalDesk.
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='PaymentOrder',
            fields=[
                ('reference', models.CharField(max_length=80, primary_key=True, serialize=False)),
                ('amount_kobo', models.PositiveIntegerField(default=40000)),
                ('currency', models.CharField(default='NGN', max_length=3)),
                ('status', models.CharField(default='PENDING', max_length=20)),
                ('provider', models.CharField(default='MONIEPOINT', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PracticalReport',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('student_name', models.CharField(max_length=160)),
                ('matric_number', models.CharField(max_length=80)),
                ('department', models.CharField(blank=True, max_length=120)),
                ('level', models.CharField(blank=True, max_length=40)),
                ('course_code', models.CharField(default='COS 101', max_length=30)),
                ('practical_title', models.CharField(default='Practical Class Summary', max_length=200)),
                ('summary', models.TextField()),
                ('c_exercises', models.TextField(blank=True)),
                ('manual_topics', models.TextField(blank=True)),
                ('conclusion', models.TextField(blank=True)),
                ('file', models.FileField(upload_to='reports/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
