from django.db import models

class Contact(models.Model):
    ROLE_CHOICES = [
        ('STUDENT', 'Student'),
        ('STAFF', 'Staff'),
        ('HOD', 'Head of Department'),
        ('PARENT', 'Parent'),
        ('OTHER', 'Other'),
    ]
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15, unique=True, help_text='With country code e.g. 919876543210')
    email = models.EmailField(blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')
    department = models.CharField(max_length=100, blank=True, default='')
    year_or_section = models.CharField(max_length=50, blank=True, default='')
    enrollment_no = models.CharField(max_length=50, blank=True, null=True, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.phone_number})"


class ContactGroup(models.Model):
    GROUP_TYPE_CHOICES = [
        ('ROLE', 'Role-based'),
        ('DEPARTMENT', 'Department-based'),
        ('CUSTOM', 'Custom'),
    ]
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, default='')
    group_type = models.CharField(max_length=15, choices=GROUP_TYPE_CHOICES, default='CUSTOM')
    members = models.ManyToManyField(Contact, related_name='groups', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.members.count()
