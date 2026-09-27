import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from broadcasts.models import BroadcastRecipient, DeliveryLog, Broadcast
from django.utils import timezone

logger = logging.getLogger(__name__)

def update_delivery_status(message_id, new_status, timestamp):
    try:
        recipient = BroadcastRecipient.objects.get(whatsapp_message_id=message_id)
        broadcast = recipient.broadcast

        status_map = {
            'sent': 'SENT',
            'delivered': 'DELIVERED',
            'read': 'READ',
            'failed': 'FAILED',
        }
        mapped_status = status_map.get(new_status, new_status.upper())

        # Only update if it's a "forward" status change
        status_order = ['PENDING', 'SENT', 'DELIVERED', 'READ', 'FAILED']
        current_idx = status_order.index(recipient.status) if recipient.status in status_order else 0
        new_idx = status_order.index(mapped_status) if mapped_status in status_order else 0

        if new_idx > current_idx or mapped_status == 'FAILED':
            old_status = recipient.status
            recipient.status = mapped_status

            if mapped_status == 'DELIVERED':
                recipient.delivered_at = timezone.now()
                broadcast.delivered_count += 1
                broadcast.save(update_fields=['delivered_count'])
            elif mapped_status == 'READ':
                if not recipient.delivered_at:
                    recipient.delivered_at = timezone.now()
                    broadcast.delivered_count += 1
                recipient.read_at = timezone.now()
                broadcast.read_count += 1
                broadcast.save(update_fields=['delivered_count', 'read_count'])
            elif mapped_status == 'FAILED':
                broadcast.failed_count += 1
                broadcast.save(update_fields=['failed_count'])

            recipient.save()

        DeliveryLog.objects.create(
            recipient=recipient,
            event=mapped_status,
            raw_payload={'message_id': message_id, 'status': new_status, 'timestamp': timestamp}
        )

    except BroadcastRecipient.DoesNotExist:
        logger.warning(f"Received status update for unknown message_id: {message_id}")
    except Exception as e:
        logger.error(f"Error updating delivery status: {e}")


@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'GET':
        verify_token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        if verify_token == settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN:
            return HttpResponse(challenge)
        return HttpResponse('Forbidden', status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    statuses = value.get('statuses', [])
                    for s in statuses:
                        update_delivery_status(
                            message_id=s.get('id', ''),
                            new_status=s.get('status', ''),
                            timestamp=s.get('timestamp', ''),
                        )
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")

        return JsonResponse({'status': 'ok'})

    return HttpResponse('Method not allowed', status=405)
