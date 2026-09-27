from django.contrib import admin
from .models import Contact, ContactGroup

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'role', 'department', 'is_active']
    list_filter = ['role', 'department', 'is_active']
    search_fields = ['name', 'phone_number', 'email']

@admin.register(ContactGroup)
class ContactGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'group_type', 'member_count', 'created_at']
    list_filter = ['group_type']
