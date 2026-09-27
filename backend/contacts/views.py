from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Contact, ContactGroup
from .serializers import (
    ContactSerializer, ContactGroupSerializer,
    ContactGroupListSerializer, ContactBulkImportSerializer
)

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'department', 'is_active', 'year_or_section']
    search_fields = ['name', 'phone_number', 'email', 'enrollment_no']
    ordering_fields = ['name', 'created_at', 'role']

    @action(detail=False, methods=['post'], url_path='bulk-import')
    def bulk_import(self, request):
        serializer = ContactBulkImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contacts_data = serializer.validated_data['contacts']
        created = 0
        errors = []
        for idx, data in enumerate(contacts_data):
            try:
                Contact.objects.update_or_create(
                    phone_number=data['phone_number'],
                    defaults={
                        'name': data.get('name', ''),
                        'role': data.get('role', 'STUDENT'),
                        'department': data.get('department', ''),
                        'year_or_section': data.get('year_or_section', ''),
                        'enrollment_no': data.get('enrollment_no'),
                        'email': data.get('email'),
                    }
                )
                created += 1
            except Exception as e:
                errors.append({'row': idx, 'error': str(e)})
        return Response({'created': created, 'errors': errors}, status=status.HTTP_201_CREATED)


class ContactGroupViewSet(viewsets.ModelViewSet):
    queryset = ContactGroup.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['group_type']
    search_fields = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return ContactGroupListSerializer
        return ContactGroupSerializer

    @action(detail=True, methods=['post'], url_path='add-members')
    def add_members(self, request, pk=None):
        group = self.get_object()
        contact_ids = request.data.get('contact_ids', [])
        contacts = Contact.objects.filter(id__in=contact_ids)
        group.members.add(*contacts)
        return Response({'added': contacts.count()})

    @action(detail=True, methods=['post'], url_path='remove-members')
    def remove_members(self, request, pk=None):
        group = self.get_object()
        contact_ids = request.data.get('contact_ids', [])
        contacts = Contact.objects.filter(id__in=contact_ids)
        group.members.remove(*contacts)
        return Response({'removed': contacts.count()})
