from rest_framework import serializers
from ai_assistant.models import (
    KnowledgeCategory,
    KnowledgeItem,
    FAQItem,
    KnowledgeDocument,
    StudentInquiryLog
)


class KnowledgeCategorySerializer(serializers.ModelSerializer):
    item_count = serializers.IntegerField(source='items.count', read_only=True)
    faq_count = serializers.IntegerField(source='faqs.count', read_only=True)

    class Meta:
        model = KnowledgeCategory
        fields = ['id', 'code', 'name', 'description', 'display_order', 'item_count', 'faq_count', 'created_at']


class KnowledgeItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_code = serializers.CharField(source='category.code', read_only=True)

    class Meta:
        model = KnowledgeItem
        fields = [
            'id', 'category', 'category_name', 'category_code',
            'title', 'content', 'tags', 'is_active', 'priority',
            'created_at', 'updated_at'
        ]


class FAQItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = FAQItem
        fields = [
            'id', 'category', 'category_name', 'question', 'answer',
            'keywords', 'is_active', 'priority', 'created_at', 'updated_at'
        ]


class KnowledgeDocumentSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = KnowledgeDocument
        fields = [
            'id', 'title', 'file', 'category', 'category_name',
            'file_type', 'extracted_text', 'is_indexed', 'uploaded_at'
        ]
        read_only_fields = ['extracted_text', 'file_type', 'uploaded_at']


class StudentInquiryLogSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='contact.name', read_only=True)
    contact_role = serializers.CharField(source='contact.role', read_only=True)

    class Meta:
        model = StudentInquiryLog
        fields = [
            'id', 'phone_number', 'contact', 'contact_name', 'contact_role',
            'question', 'detected_intent', 'retrieved_context', 'answer',
            'status', 'source', 'latency_ms', 'created_at'
        ]
