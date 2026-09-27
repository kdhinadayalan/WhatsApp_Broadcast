from django.contrib import admin
from .models import MessageTemplate

@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'meta_template_name', 'category', 'language', 'status', 'param_count']
    list_filter = ['category', 'status', 'language']
    search_fields = ['name', 'meta_template_name']
