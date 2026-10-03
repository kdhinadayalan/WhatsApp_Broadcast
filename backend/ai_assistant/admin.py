from django.contrib import admin
from ai_assistant.models import (
    KnowledgeCategory,
    KnowledgeItem,
    FAQItem,
    KnowledgeDocument,
    StudentInquiryLog
)


@admin.register(KnowledgeCategory)
class KnowledgeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'display_order', 'created_at')
    search_fields = ('name', 'code')
    ordering = ('display_order',)


@admin.register(KnowledgeItem)
class KnowledgeItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_active', 'priority', 'updated_at')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'content', 'tags')
    ordering = ('-priority', 'title')


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'is_active', 'priority', 'updated_at')
    list_filter = ('category', 'is_active')
    search_fields = ('question', 'answer', 'keywords')
    ordering = ('-priority',)


@admin.register(KnowledgeDocument)
class KnowledgeDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'file_type', 'is_indexed', 'uploaded_at')
    list_filter = ('category', 'is_indexed')
    search_fields = ('title', 'extracted_text')


@admin.register(StudentInquiryLog)
class StudentInquiryLogAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'contact', 'status', 'source', 'latency_ms', 'created_at')
    list_filter = ('status', 'source', 'created_at')
    search_fields = ('phone_number', 'question', 'answer', 'detected_intent')
    readonly_fields = ('phone_number', 'contact', 'question', 'detected_intent', 'retrieved_context', 'answer', 'status', 'source', 'latency_ms', 'created_at')
