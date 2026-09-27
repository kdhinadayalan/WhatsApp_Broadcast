from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import MessageTemplate
from .serializers import MessageTemplateSerializer

class MessageTemplateViewSet(viewsets.ModelViewSet):
    queryset = MessageTemplate.objects.all()
    serializer_class = MessageTemplateSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'status', 'language']
    search_fields = ['name', 'meta_template_name', 'body_text']

    @action(detail=False, methods=['get'], url_path='sync')
    def sync_from_meta(self, request):
        """Placeholder: sync templates from Meta WhatsApp Business Account."""
        # TODO: implement actual sync with Meta Graph API
        return Response({'message': 'Template sync is not yet implemented. Add templates manually for now.'})
