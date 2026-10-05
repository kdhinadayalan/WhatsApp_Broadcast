import os
from pathlib import Path
from rest_framework import viewsets, filters, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings

from ai_assistant.models import (
    KnowledgeCategory,
    KnowledgeItem,
    FAQItem,
    KnowledgeDocument,
    StudentInquiryLog
)
from ai_assistant.serializers import (
    KnowledgeCategorySerializer,
    KnowledgeItemSerializer,
    FAQItemSerializer,
    KnowledgeDocumentSerializer,
    StudentInquiryLogSerializer
)
from ai_assistant.services.rag_service import extract_text_from_file, sync_knowledge_to_workspace
from ai_assistant.services.inquiry_handler import handle_student_inquiry


class KnowledgeCategoryViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeCategory.objects.all()
    serializer_class = KnowledgeCategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['display_order', 'name']


class KnowledgeItemViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeItem.objects.all().select_related('category')
    serializer_class = KnowledgeItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'category__code', 'is_active']
    search_fields = ['title', 'content', 'tags']
    ordering_fields = ['priority', 'updated_at', 'title']

    def perform_create(self, serializer):
        item = serializer.save()
        # Auto-sync workspace markdown
        try:
            sync_knowledge_to_workspace(settings.BASE_DIR / "openclaw_college_agent")
        except Exception:
            pass

    def perform_update(self, serializer):
        item = serializer.save()
        try:
            sync_knowledge_to_workspace(settings.BASE_DIR / "openclaw_college_agent")
        except Exception:
            pass

    def perform_destroy(self, instance):
        instance.delete()
        try:
            sync_knowledge_to_workspace(settings.BASE_DIR / "openclaw_college_agent")
        except Exception:
            pass


class FAQItemViewSet(viewsets.ModelViewSet):
    queryset = FAQItem.objects.all().select_related('category')
    serializer_class = FAQItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['question', 'answer', 'keywords']
    ordering_fields = ['priority', 'updated_at', 'question']

    def perform_create(self, serializer):
        serializer.save()
        try:
            sync_knowledge_to_workspace(settings.BASE_DIR / "openclaw_college_agent")
        except Exception:
            pass

    def perform_update(self, serializer):
        serializer.save()
        try:
            sync_knowledge_to_workspace(settings.BASE_DIR / "openclaw_college_agent")
        except Exception:
            pass

    def perform_destroy(self, instance):
        instance.delete()
        try:
            sync_knowledge_to_workspace(settings.BASE_DIR / "openclaw_college_agent")
        except Exception:
            pass


class KnowledgeDocumentViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeDocument.objects.all().select_related('category')
    serializer_class = KnowledgeDocumentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'is_indexed']
    search_fields = ['title', 'extracted_text']

    def perform_create(self, serializer):
        doc = serializer.save()
        if doc.file:
            doc.file_type = Path(doc.file.name).suffix.lower()
            file_path = doc.file.path
            doc.extracted_text = extract_text_from_file(file_path)
            doc.save(update_fields=['file_type', 'extracted_text'])


class StudentInquiryLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StudentInquiryLog.objects.all().select_related('contact')
    serializer_class = StudentInquiryLogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'source']
    search_fields = ['phone_number', 'question', 'answer', 'detected_intent']
    ordering_fields = ['created_at', 'latency_ms']


@api_view(['POST'])
def chat_simulator(request):
    """
    Simulate an incoming student inquiry from the React admin dashboard.
    Does not dispatch external WhatsApp messages.
    """
    question = request.data.get('question', '').strip()
    phone_number = request.data.get('phone_number', '919876543210')

    if not question:
        return Response({'error': 'Question is required'}, status=status.HTTP_400_BAD_REQUEST)

    result = handle_student_inquiry(
        phone_number=phone_number,
        question=question,
        source='SIMULATOR',
        send_whatsapp_reply=False
    )
    return Response(result)


@api_view(['POST'])
def sync_agent_knowledge(request):
    """Sync all active DB knowledge items and FAQs to OpenClaw workspace markdown."""
    workspace_dir = settings.BASE_DIR / "openclaw_college_agent"
    try:
        sync_knowledge_to_workspace(workspace_dir)
        return Response({
            'status': 'success',
            'message': f'Knowledge base successfully synchronized to {workspace_dir}',
            'item_count': KnowledgeItem.objects.filter(is_active=True).count(),
            'faq_count': FAQItem.objects.filter(is_active=True).count(),
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def ai_assistant_stats(request):
    """Get high-level summary statistics for the AI Assistant."""
    total_inquiries = StudentInquiryLog.objects.count()
    answered_count = StudentInquiryLog.objects.filter(status='ANSWERED').count()
    fallback_count = StudentInquiryLog.objects.filter(status='FALLBACK').count()
    error_count = StudentInquiryLog.objects.filter(status='ERROR').count()

    return Response({
        'total_inquiries': total_inquiries,
        'answered_count': answered_count,
        'fallback_count': fallback_count,
        'error_count': error_count,
        'answered_percentage': round((answered_count / total_inquiries * 100), 1) if total_inquiries > 0 else 0,
        'total_knowledge_items': KnowledgeItem.objects.count(),
        'active_knowledge_items': KnowledgeItem.objects.filter(is_active=True).count(),
        'total_faqs': FAQItem.objects.count(),
        'total_documents': KnowledgeDocument.objects.count(),
    })


@api_view(['GET'])
def openclaw_status(request):
    """Inspect and report OpenClaw connection, gateway status, and workspace health."""
    from ai_assistant.services.openclaw_service import inspect_openclaw_status
    status_info = inspect_openclaw_status()
    return Response(status_info)
