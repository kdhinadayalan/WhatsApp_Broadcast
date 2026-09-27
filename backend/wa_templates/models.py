from django.db import models

class MessageTemplate(models.Model):
    CATEGORY_CHOICES = [
        ('UTILITY', 'Utility'),
        ('MARKETING', 'Marketing'),
        ('AUTHENTICATION', 'Authentication'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    name = models.CharField(max_length=200, help_text='Display name')
    meta_template_name = models.CharField(max_length=200, unique=True, help_text='Name registered with Meta')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='UTILITY')
    language = models.CharField(max_length=10, default='en')
    header_text = models.CharField(max_length=500, blank=True, default='')
    body_text = models.TextField(help_text='Template body. Use {{1}}, {{2}} etc for variables')
    footer_text = models.CharField(max_length=200, blank=True, default='')
    param_count = models.IntegerField(default=0, help_text='Number of {{N}} placeholders in body')
    sample_params = models.JSONField(default=list, blank=True, help_text='Sample values for parameters')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.status})"
