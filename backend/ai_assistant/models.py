from django.db import models
from contacts.models import Contact


class KnowledgeCategory(models.Model):
    CATEGORY_TYPES = [
        ('GENERAL', 'General Information'),
        ('DEPARTMENTS', 'Departments & Courses'),
        ('FACULTY', 'Faculty & HODs'),
        ('ADMISSIONS', 'Admissions & Eligibility'),
        ('FEES', 'Fees & Scholarships'),
        ('EXAMS', 'Examinations & Results'),
        ('CALENDAR', 'Academic Calendar & Dates'),
        ('TIMINGS', 'College Timings'),
        ('CONTACTS', 'Contact & Office Hours'),
        ('RULES', 'Rules & Regulations'),
        ('FACILITIES', 'Campus Facilities & Labs'),
        ('HOSTEL', 'Hostel & Mess'),
        ('EVENTS', 'Events & Activities'),
        ('PLACEMENTS', 'Placements & Careers'),
        ('FAQ', 'Frequently Asked Questions'),
    ]

    code = models.CharField(max_length=50, choices=CATEGORY_TYPES, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, default='')
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name_plural = 'Knowledge Categories'

    def __str__(self):
        return f"{self.name} ({self.code})"


class KnowledgeItem(models.Model):
    category = models.ForeignKey(KnowledgeCategory, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=255)
    content = models.TextField(help_text='Detailed information, facts, lists, or instructions.')
    tags = models.CharField(max_length=255, blank=True, default='', help_text='Comma-separated keywords e.g. mca, hod, subjects')
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text='Higher priority items are ranked first in search')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'title']

    def __str__(self):
        return f"[{self.category.code}] {self.title}"


class FAQItem(models.Model):
    category = models.ForeignKey(KnowledgeCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='faqs')
    question = models.CharField(max_length=300)
    answer = models.TextField()
    keywords = models.CharField(max_length=255, blank=True, default='', help_text='Comma-separated search phrases')
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'question']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question


class KnowledgeDocument(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='knowledge_docs/')
    category = models.ForeignKey(KnowledgeCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    file_type = models.CharField(max_length=50, blank=True, default='')
    extracted_text = models.TextField(blank=True, default='', help_text='Text automatically parsed from document')
    is_indexed = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title


class StudentInquiryLog(models.Model):
    STATUS_CHOICES = [
        ('ANSWERED', 'Answered'),
        ('FALLBACK', 'Fallback (No Info)'),
        ('ERROR', 'Error'),
    ]

    SOURCE_CHOICES = [
        ('WHATSAPP', 'WhatsApp'),
        ('SIMULATOR', 'Web Simulator'),
    ]

    phone_number = models.CharField(max_length=25)
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_inquiries')
    question = models.TextField()
    detected_intent = models.CharField(max_length=150, blank=True, default='')
    retrieved_context = models.TextField(blank=True, default='')
    answer = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ANSWERED')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='WHATSAPP')
    latency_ms = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.phone_number} - {self.question[:30]}... ({self.status})"
