import time
import logging
from django.utils import timezone
from contacts.models import Contact
from whatsapp_integration.client import WhatsAppClient
from ai_assistant.models import StudentInquiryLog
from ai_assistant.services.rag_service import search_knowledge_base, format_retrieved_context
from ai_assistant.services.openclaw_service import ask_college_assistant, FALLBACK_MESSAGE

logger = logging.getLogger(__name__)


def handle_student_inquiry(
    phone_number: str,
    question: str,
    source: str = 'WHATSAPP',
    send_whatsapp_reply: bool = True
) -> dict:
    """
    Main pipeline for processing an incoming student inquiry:
    1. Resolve contact if registered.
    2. Search Knowledge Base (RAG).
    3. Generate grounded answer via OpenClaw / AI Assistant.
    4. Send reply via WhatsApp if requested.
    5. Log inquiry in database.
    """
    start_time = time.time()
    clean_question = question.strip()

    # 1. Match Contact
    cleaned_phone = phone_number.replace('+', '').replace(' ', '').replace('-', '')
    contact = None
    try:
        contact = Contact.objects.filter(phone_number__endswith=cleaned_phone[-10:]).first()
    except Exception as e:
        logger.warning(f"Error querying contact for phone {cleaned_phone}: {e}")

    student_name = contact.name if contact else ""

    # 2. Retrieve context from Knowledge Base
    search_results = search_knowledge_base(clean_question, top_k=5)
    retrieved_context = format_retrieved_context(search_results)

    # Detect high-level intent/category from top result if available
    detected_intent = search_results[0]['category'] if search_results else "General"

    # 3. Ask College Assistant
    best_match = search_results[0] if search_results else None
    ai_result = ask_college_assistant(
        student_question=clean_question,
        retrieved_context=retrieved_context,
        student_name=student_name,
        best_match=best_match
    )

    answer = ai_result["answer"]
    status = ai_result["status"]
    latency_ms = int((time.time() - start_time) * 1000)

    # 4. Dispatch WhatsApp message if source is WhatsApp
    whatsapp_sent = False
    if send_whatsapp_reply and source == 'WHATSAPP' and phone_number:
        try:
            client = WhatsAppClient()
            client.send_text_message(to_phone=phone_number, text=answer)
            whatsapp_sent = True
            logger.info(f"Sent WhatsApp AI response to {phone_number}")
        except Exception as e:
            logger.error(f"Failed to send WhatsApp response to {phone_number}: {e}")

    # 5. Log Inquiry
    log_entry = StudentInquiryLog.objects.create(
        phone_number=phone_number,
        contact=contact,
        question=clean_question,
        detected_intent=detected_intent,
        retrieved_context=retrieved_context,
        answer=answer,
        status=status,
        source=source,
        latency_ms=latency_ms,
    )

    return {
        "id": log_entry.id,
        "phone_number": phone_number,
        "student_name": student_name,
        "question": clean_question,
        "answer": answer,
        "status": status,
        "intent": detected_intent,
        "retrieved_context": retrieved_context,
        "sources": [
            {
                "title": r["title"],
                "type": r["type"],
                "category": r["category"],
                "score": r["score"],
            }
            for r in search_results
        ],
        "latency_ms": latency_ms,
        "whatsapp_sent": whatsapp_sent,
        "created_at": log_entry.created_at.isoformat(),
    }
