from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ai_assistant import views

router = DefaultRouter()
router.register(r'categories', views.KnowledgeCategoryViewSet, basename='knowledge-category')
router.register(r'items', views.KnowledgeItemViewSet, basename='knowledge-item')
router.register(r'faqs', views.FAQItemViewSet, basename='faq-item')
router.register(r'documents', views.KnowledgeDocumentViewSet, basename='knowledge-document')
router.register(r'inquiries', views.StudentInquiryLogViewSet, basename='student-inquiry')

urlpatterns = [
    path('', include(router.urls)),
    path('chat/', views.chat_simulator, name='ai-chat-simulator'),
    path('sync-agent/', views.sync_agent_knowledge, name='ai-sync-agent'),
    path('stats/', views.ai_assistant_stats, name='ai-assistant-stats'),
    path('openclaw-status/', views.openclaw_status, name='openclaw-status'),
]
