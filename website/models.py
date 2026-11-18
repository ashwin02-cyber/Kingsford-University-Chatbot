from django.db import models
from django.db.models import Q, F, CheckConstraint

class Department(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField()
    head_name = models.CharField(max_length=120, null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Programme(models.Model):
    LEVEL_CHOICES = [
        ('UG', 'Undergraduate'),
        ('PG', 'Postgraduate'),
    ]

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programmes')
    name = models.CharField(max_length=150)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    duration = models.CharField(max_length=50)
    eligibility = models.TextField()
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['level', 'name']
        constraints = [
            models.UniqueConstraint(fields=['department', 'name'], name='unique_department_programme')
        ]

    def __str__(self):
        return f"{self.name} ({self.level})"


class AdmissionInfo(models.Model):
    CATEGORY_CHOICES = [
        ('procedure', 'Procedure'),
        ('eligibility', 'Eligibility'),
        ('deadline', 'Deadline'),
        ('document', 'Document'),
        ('faq', 'FAQ'),
    ]

    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    deadline_date = models.DateField(null=True, blank=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name_plural = 'Admission info'

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"


class FeeInfo(models.Model):
    programme = models.ForeignKey(Programme, on_delete=models.SET_NULL, null=True, blank=True, related_name='fees')
    fee_type = models.CharField(max_length=80)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='INR')
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['programme', 'fee_type']
        verbose_name_plural = 'Fee info'

    def __str__(self):
        prog = self.programme.name if self.programme else "General"
        return f"{prog} - {self.fee_type}: {self.currency} {self.amount if self.amount is not None else 'N/A'}"


class Announcement(models.Model):
    CATEGORY_CHOICES = [
        ('General', 'General'),
        ('Examination', 'Examination'),
        ('Admission', 'Admission'),
    ]

    title = models.CharField(max_length=200)
    body = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    published_at = models.DateTimeField(db_index=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return f"[{self.category}] {self.title}"


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    venue = models.CharField(max_length=200)
    start_datetime = models.DateTimeField(db_index=True)
    end_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['start_datetime']
        constraints = [
            CheckConstraint(
                condition=Q(end_datetime__isnull=True) | Q(end_datetime__gte=F('start_datetime')),
                name='check_event_end_after_start'
            )
        ]

    def __str__(self):
        return f"{self.title} ({self.start_datetime.strftime('%Y-%m-%d')})"


class KnowledgeDocument(models.Model):
    TOPIC_CHOICES = [
        ('overview', 'University Overview'),
        ('vision_mission', 'Vision & Mission'),
        ('history', 'History'),
        ('leadership', 'Leadership & Administration'),
        ('accreditation', 'Accreditation & Achievements'),
        ('calendar', 'Academic Calendar'),
        ('exams', 'Examinations'),
        ('hostel', 'Hostel & Accommodation'),
        ('scholarship', 'Scholarships & Financial Aid'),
        ('library', 'Library & Learning Resources'),
        ('facilities', 'Campus Facilities & Labs'),
        ('contact', 'Contact Information'),
    ]

    topic = models.CharField(max_length=50, choices=TOPIC_CHOICES, db_index=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    keywords = models.CharField(max_length=255, help_text="Comma-separated keywords for retrieval")
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['topic', 'title']

    def __str__(self):
        return f"[{self.get_topic_display()}] {self.title}"
