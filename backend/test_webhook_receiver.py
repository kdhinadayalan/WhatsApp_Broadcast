import json
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nmc_college.settings')
django.setup()

from django.test import Client
from ai_assistant.models import StudentInquiryLog

client = Client()

webhook_payload = {
    "entry": [
        {
            "changes": [
                {
                    "value": {
                        "messages": [
                            {
                                "from": "919865891210",
                                "id": "wamid.TEST_STUDENT_MESSAGE_001",
                                "timestamp": "1727932800",
                                "type": "text",
                                "text": {
                                    "body": "What are the college timings?"
                                }
                            }
                        ]
                    }
                }
            ]
        }
    ]
}

print("Simulating Meta WhatsApp Webhook POST...")
response = client.post(
    '/api/webhooks/whatsapp/',
    data=json.dumps(webhook_payload),
    content_type='application/json'
)

print(f"Webhook HTTP Response Code: {response.status_code}")
print(f"Webhook Response Body: {response.json()}")

latest_inquiry = StudentInquiryLog.objects.filter(phone_number='919865891210').first()
if latest_inquiry:
    print("\nVerified in Database:")
    print(f"Phone   : {latest_inquiry.phone_number}")
    print(f"Question: {latest_inquiry.question}")
    print(f"Status  : {latest_inquiry.status}")
    print(f"Answer  :\n{latest_inquiry.answer}")
else:
    print("No inquiry logged.")
