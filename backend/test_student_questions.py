import os
import sys
import django

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nmc_college.settings')
django.setup()

from ai_assistant.services.inquiry_handler import handle_student_inquiry

questions = [
    "Who is the HOD of MCA?",
    "What is the college address?",
    "What are the MCA subjects?",
    "When does the semester start?",
    "What is the exam fee?",
    "What documents are required for admission?",
    "Tell me about the college departments.",
    "What are the college timings?",
    "Who won the 1994 FIFA world cup?", # Unanswerable test
]

print("=" * 60)
print("TESTING ALL 8 STUDENT QUESTIONS + 1 GUARDRAIL TEST")
print("=" * 60)

for i, q in enumerate(questions, 1):
    print(f"\n[{i}] Question: {q}")
    result = handle_student_inquiry(
        phone_number="919876543210",
        question=q,
        source="SIMULATOR",
        send_whatsapp_reply=False
    )
    print(f"Status : {result['status']}")
    print(f"Intent : {result['intent']}")
    print(f"Latency: {result['latency_ms']}ms")
    print(f"Answer :\n{result['answer']}")
    print("-" * 60)
