from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count
from contacts.models import Contact
from .models import Broadcast, BroadcastRecipient, AuditLog
from .serializers import (
    BroadcastListSerializer, BroadcastCreateSerializer,
    BroadcastDetailSerializer, BroadcastRecipientSerializer,
    AuditLogSerializer
)

class BroadcastViewSet(viewsets.ModelViewSet):
    queryset = Broadcast.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['created_at', 'status']

    def get_serializer_class(self):
        if self.action == 'list':
            return BroadcastListSerializer
        if self.action == 'create':
            return BroadcastCreateSerializer
        return BroadcastDetailSerializer

    @action(detail=True, methods=['post'], url_path='send')
    def send_broadcast(self, request, pk=None):
        broadcast = self.get_object()
        if broadcast.status not in ['DRAFT', 'FAILED']:
            return Response(
                {'error': f'Cannot send broadcast with status {broadcast.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get all unique active contacts from selected groups
        contacts = Contact.objects.filter(
            groups__in=broadcast.groups.all(),
            is_active=True
        ).distinct()

        if not contacts.exists():
            return Response(
                {'error': 'No active contacts found in selected groups'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create recipient records
        broadcast.status = 'SENDING'
        broadcast.started_at = timezone.now()
        broadcast.total_recipients = contacts.count()
        broadcast.sent_count = 0
        broadcast.delivered_count = 0
        broadcast.read_count = 0
        broadcast.failed_count = 0
        broadcast.save()

        recipients_created = 0
        for contact in contacts:
            _, created = BroadcastRecipient.objects.get_or_create(
                broadcast=broadcast,
                contact=contact,
                defaults={'status': 'PENDING'}
            )
            if created:
                recipients_created += 1

        # Queue the actual sending via background thread or Celery
        try:
            import threading
            from .tasks import process_broadcast_sync
            threading.Thread(target=process_broadcast_sync, args=(broadcast.id,), daemon=True).start()
        except Exception as e:
            from .tasks import process_broadcast_sync
            process_broadcast_sync(broadcast.id)

        AuditLog.objects.create(
            broadcast=broadcast,
            action='BROADCAST_STARTED',
            details=f'Broadcast queued for {recipients_created} recipients'
        )

        return Response({
            'message': 'Broadcast started',
            'total_recipients': broadcast.total_recipients,
            'status': broadcast.status
        })

    @action(detail=True, methods=['get'], url_path='recipients')
    def list_recipients(self, request, pk=None):
        broadcast = self.get_object()
        recipients = broadcast.recipients.select_related('contact').all()
        status_filter = request.query_params.get('status')
        if status_filter:
            recipients = recipients.filter(status=status_filter)
        serializer = BroadcastRecipientSerializer(recipients, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='status')
    def broadcast_status(self, request, pk=None):
        broadcast = self.get_object()
        return Response({
            'id': broadcast.id,
            'title': broadcast.title,
            'status': broadcast.status,
            'total_recipients': broadcast.total_recipients,
            'sent_count': broadcast.sent_count,
            'delivered_count': broadcast.delivered_count,
            'read_count': broadcast.read_count,
            'failed_count': broadcast.failed_count,
            'delivery_rate': broadcast.delivery_rate,
            'started_at': broadcast.started_at,
            'completed_at': broadcast.completed_at,
        })

    @action(detail=True, methods=['post'], url_path='retry-failed')
    def retry_failed(self, request, pk=None):
        broadcast = self.get_object()
        failed_recipients = broadcast.recipients.filter(status='FAILED')
        count = failed_recipients.count()
        failed_recipients.update(status='PENDING', error_message='')
        broadcast.status = 'SENDING'
        broadcast.save()

        try:
            import threading
            from .tasks import process_broadcast_sync
            threading.Thread(target=process_broadcast_sync, args=(broadcast.id,), daemon=True).start()
        except Exception:
            from .tasks import process_broadcast_sync
            process_broadcast_sync(broadcast.id)

        return Response({'message': f'Retrying {count} failed messages'})

from rest_framework.decorators import api_view

@api_view(['GET'])
def dashboard_stats(request):
    from django.db.models import Sum
    total_contacts = Contact.objects.filter(is_active=True).count()
    total_broadcasts = Broadcast.objects.count()
    aggregate = Broadcast.objects.aggregate(
        total_sent=Sum('sent_count'),
        total_delivered=Sum('delivered_count'),
        total_read=Sum('read_count'),
        total_failed=Sum('failed_count'),
    )
    recent_broadcasts = BroadcastListSerializer(
        Broadcast.objects.all()[:5], many=True
    ).data

    return Response({
        'total_contacts': total_contacts,
        'total_broadcasts': total_broadcasts,
        'total_sent': aggregate['total_sent'] or 0,
        'total_delivered': aggregate['total_delivered'] or 0,
        'total_read': aggregate['total_read'] or 0,
        'total_failed': aggregate['total_failed'] or 0,
        'recent_broadcasts': recent_broadcasts,
        'contacts_by_role': list(
            Contact.objects.filter(is_active=True)
            .values('role')
            .annotate(count=Count('id'))
            .order_by('role')
        ),
    })
