from django.db import models
from contacts.models import Contact, ContactGroup
from wa_templates.models import MessageTemplate

class Broadcast(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('QUEUED', 'Queued'),
        ('SENDING', 'Sending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    title = models.CharField(max_length=300)
    template = models.ForeignKey(MessageTemplate, on_delete=models.PROTECT, related_name='broadcasts')
    template_params = models.JSONField(default=list, blank=True, help_text='Values for template parameters {{1}}, {{2}}, etc.')
    groups = models.ManyToManyField(ContactGroup, related_name='broadcasts', blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='DRAFT')
    total_recipients = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    read_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.status})"

    @property
    def delivery_rate(self):
        if self.total_recipients == 0:
            return 0
        return round((self.delivered_count / self.total_recipients) * 100, 1)


class BroadcastRecipient(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('READ', 'Read'),
        ('FAILED', 'Failed'),
    ]
    broadcast = models.ForeignKey(Broadcast, on_delete=models.CASCADE, related_name='recipients')
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='broadcast_messages')
    whatsapp_message_id = models.CharField(max_length=200, blank=True, default='')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    error_message = models.TextField(blank=True, default='')
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['broadcast', 'contact']
        ordering = ['contact__name']

    def __str__(self):
        return f"{self.contact.name} - {self.status}"


class DeliveryLog(models.Model):
    EVENT_CHOICES = [
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('READ', 'Read'),
        ('FAILED', 'Failed'),
    ]
    recipient = models.ForeignKey(BroadcastRecipient, on_delete=models.CASCADE, related_name='logs')
    event = models.CharField(max_length=15, choices=EVENT_CHOICES)
    raw_payload = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']


class AuditLog(models.Model):
    broadcast = models.ForeignKey(Broadcast, on_delete=models.CASCADE, related_name='audit_logs', null=True, blank=True)
    action = models.CharField(max_length=200)
    performed_by = models.CharField(max_length=200, default='system')
    details = models.TextField(blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
