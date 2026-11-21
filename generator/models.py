import uuid
from django.db import models

class PaymentOrder(models.Model):
    PLAN_CHOICES = [("FOUR_DOCS", "4 Documents")]
    reference = models.CharField(max_length=80, primary_key=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="FOUR_DOCS")
    amount_kobo = models.PositiveIntegerField(default=45000)
    max_documents = models.PositiveSmallIntegerField(default=4)
    currency = models.CharField(max_length=3, default="NGN")
    status = models.CharField(
        max_length=20,
        choices=[("PENDING", "Awaiting receipt"), ("UNDER_REVIEW", "Under review"),
                 ("APPROVED", "Approved"), ("REJECTED", "Rejected")],
        default="PENDING",
    )
    provider = models.CharField(max_length=20, default="OPAY")
    receipt = models.FileField(upload_to="payment_receipts/", blank=True, null=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    admin_note = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.reference} - {self.plan} - {self.status}"

class PracticalReport(models.Model):
    TYPE_CHOICES = [("SUMMARY", "Practical Class Summary"), ("EXERCISES", "Practical Exercises")]
    EXERCISE_TEMPLATE_CHOICES = [("CLASSIC_SAMPLE", "Classic Student Template"), ("SIMPLE_SAMPLE", "Simple COS 101 Template")]
    PLAN_CHOICES = [("FOUR_DOCS", "4 Documents")]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_order = models.ForeignKey(PaymentOrder, null=True, blank=True, on_delete=models.PROTECT, related_name="reports")
    assignment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="SUMMARY")
    exercise_template = models.CharField(max_length=24, choices=EXERCISE_TEMPLATE_CHOICES, default="CLASSIC_SAMPLE")
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="STANDARD")
    student_name = models.CharField(max_length=160)
    matric_number = models.CharField(max_length=80)
    department = models.CharField(max_length=120, blank=True)
    course_code = models.CharField(max_length=30, default="COS 101")
    course_title = models.CharField(max_length=160, blank=True)
    level = models.CharField(max_length=40, blank=True)
    lecturer = models.CharField(max_length=160, blank=True)
    practical_title = models.CharField(max_length=200, default="Practical Class Summary")
    summary = models.TextField(blank=True)
    c_exercises = models.TextField(blank=True)
    manual_topics = models.TextField(blank=True)
    conclusion = models.TextField(blank=True)
    application_letter = models.TextField(blank=True)
    cv_content = models.TextField(blank=True)
    saving_steps = models.TextField(blank=True)
    extra_notes = models.TextField(blank=True)
    ai_generated = models.BooleanField(default=False)
    file = models.FileField(upload_to="reports/")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.student_name} - {self.assignment_type}"

class DailyDownload(models.Model):
    report = models.ForeignKey(PracticalReport, on_delete=models.CASCADE, related_name="daily_downloads")
    download_date = models.DateField()
    count = models.PositiveSmallIntegerField(default=0)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["report", "download_date"], name="unique_report_download_day")]
