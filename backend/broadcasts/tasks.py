import time
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    def shared_task(*args, **kwargs):
        def decorator(func):
            func.delay = lambda *a, **kw: func(*a, **kw)
            return func
        return decorator


def _send_single_message(recipient):
    """Send a single WhatsApp message via Meta Cloud API."""
    from whatsapp_integration.client import WhatsAppClient

    client = WhatsAppClient()
    broadcast = recipient.broadcast

    try:
        # Build components from template params
        components = []
        if broadcast.template_params:
            body_params = []
            for param_value in broadcast.template_params:
                body_params.append({"type": "text", "text": str(param_value)})
            if body_params:
                components.append({"type": "body", "parameters": body_params})

        result = client.send_template_message(
            to_phone=recipient.contact.phone_number,
            template_name=broadcast.template.meta_template_name,
            language=broadcast.template.language,
            components=components if components else None,
        )

        if 'messages' in result:
            recipient.whatsapp_message_id = result['messages'][0]['id']
            recipient.status = 'SENT'
            recipient.sent_at = timezone.now()
            recipient.save()

            broadcast.sent_count += 1
            broadcast.save(update_fields=['sent_count'])
            return True
        else:
            error_msg = result.get('error', {}).get('message', str(result))
            recipient.status = 'FAILED'
            recipient.error_message = error_msg
            recipient.save()

            broadcast.failed_count += 1
            broadcast.save(update_fields=['failed_count'])
            return False

    except Exception as e:
        logger.error(f"Failed to send to {recipient.contact.phone_number}: {e}")
        recipient.status = 'FAILED'
        recipient.error_message = str(e)
        recipient.save()

        broadcast.failed_count += 1
        broadcast.save(update_fields=['failed_count'])
        return False


def process_broadcast_sync(broadcast_id):
    """Process broadcast synchronously (when Celery is not available)."""
    from .models import Broadcast, BroadcastRecipient

    broadcast = Broadcast.objects.get(id=broadcast_id)
    pending = broadcast.recipients.filter(status='PENDING')

    for recipient in pending:
        _send_single_message(recipient)
        time.sleep(0.5)  # Rate limiting

    broadcast.refresh_from_db()
    broadcast.status = 'COMPLETED'
    broadcast.completed_at = timezone.now()
    broadcast.save()


@shared_task
def process_broadcast(broadcast_id):
    """Process broadcast asynchronously via Celery."""
    process_broadcast_sync(broadcast_id)


@shared_task
def send_single_message_task(recipient_id):
    """Send a single message (used for retries)."""
    from .models import BroadcastRecipient
    recipient = BroadcastRecipient.objects.select_related(
        'broadcast__template', 'contact'
    ).get(id=recipient_id)
    _send_single_message(recipient)
