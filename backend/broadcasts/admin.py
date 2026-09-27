from django.contrib import admin
from .models import Broadcast, BroadcastRecipient, DeliveryLog, AuditLog

@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ['title', 'template', 'status', 'total_recipients', 'sent_count',
                    'delivered_count', 'failed_count', 'created_at']
    list_filter = ['status']
    search_fields = ['title']

@admin.register(BroadcastRecipient)
class BroadcastRecipientAdmin(admin.ModelAdmin):
    list_display = ['broadcast', 'contact', 'status', 'sent_at', 'delivered_at']
    list_filter = ['status']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['broadcast', 'action', 'performed_by', 'timestamp']

admin.site.register(DeliveryLog)
