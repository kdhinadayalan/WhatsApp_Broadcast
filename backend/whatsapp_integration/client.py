import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class WhatsAppClient:
    BASE_URL = "https://graph.facebook.com"

    def __init__(self):
        self.api_version = settings.WHATSAPP_API_VERSION
        self.phone_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.token = settings.WHATSAPP_ACCESS_TOKEN
        self.url = f"{self.BASE_URL}/{self.api_version}/{self.phone_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def send_template_message(self, to_phone, template_name, language='en', components=None):
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language},
            }
        }
        if components:
            payload["template"]["components"] = components

        logger.info(f"Sending template '{template_name}' to {to_phone}")
        response = requests.post(self.url, json=payload, headers=self.headers, timeout=30)
        result = response.json()

        if response.status_code != 200:
            logger.error(f"WhatsApp API error: {result}")
        else:
            logger.info(f"Message sent successfully: {result}")

        return result

    def send_text_message(self, to_phone, text):
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "text",
            "text": {"body": text}
        }
        response = requests.post(self.url, json=payload, headers=self.headers, timeout=30)
        return response.json()
