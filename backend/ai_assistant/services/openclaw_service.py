import os
import sys
import json
import logging
import subprocess
import requests
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

FALLBACK_MESSAGE = "I don't have this information currently. Please contact the college office for the correct details."

AGENT_NAME = "college_assistant"
WORKSPACE_DIR = settings.BASE_DIR / "openclaw_college_agent"
OPENCLAW_CMD = r"C:\Users\Bhuva\AppData\Roaming\npm\openclaw.cmd"

SYSTEM_INSTRUCTION = """You are the official WhatsApp College AI Assistant for NMC College.
Your mission is to help students, parents, and staff by answering questions about college departments, HODs, faculty, courses, admissions, fees, exams, academic calendar, timings, facilities, hostel, events, rules, and contact info.

CRITICAL INSTRUCTIONS:
1. Grounding: Answer ONLY based on the provided COLLEGE KNOWLEDGE BASE context below.
2. ZERO Hallucination: Do NOT invent, assume, or fabricate any college information, dates, fees, contact numbers, or policies.
3. Unavailability Rule: If the answer is NOT present in the provided context or if you are not certain, you MUST reply with this EXACT text and nothing else:
"I don't have this information currently. Please contact the college office for the correct details."
4. WhatsApp Formatting: Use WhatsApp-friendly styling:
   - *Bold* important names, headings, dates, or fees (single asterisks: *text*).
   - Use clean bullet points (• ) for lists.
   - Keep answers short, clear, polite, and student-friendly.
"""


def get_agent_workspace() -> Path:
    """Ensure the agent workspace directory exists with required config files."""
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    identity_file = WORKSPACE_DIR / "IDENTITY.md"
    if not identity_file.exists():
        identity_file.write_text(
            "# IDENTITY.md - Who Am I?\n\n"
            "- **Name:** NMC College Assistant\n"
            "- **Creature:** College Student Companion\n"
            "- **Vibe:** Clear, accurate, student-friendly, and polite\n"
            "- **Emoji:** 🎓\n"
            "- **Role:** Official WhatsApp AI Assistant for NMC College\n",
            encoding="utf-8"
        )

    soul_file = WORKSPACE_DIR / "SOUL.md"
    if not soul_file.exists():
        soul_file.write_text(
            f"# SOUL.md - Operational Guardrails\n\n"
            f"1. You are the AI Assistant for NMC College.\n"
            f"2. Strict Knowledge Grounding: Never make up dates, fees, HOD names, or course information.\n"
            f"3. When facts are missing from knowledge context, reply strictly:\n"
            f"\"{FALLBACK_MESSAGE}\"\n"
            f"4. Keep responses structured, concise, and formatted for WhatsApp.\n",
            encoding="utf-8"
        )
    return WORKSPACE_DIR


def generate_with_gemini_direct(prompt: str) -> str:
    """Direct Google Gemini API fallback using the configured GEMINI_API_KEY / GOOGLE_API_KEY."""
    api_key = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
    if not api_key:
        logger.warning("No GEMINI_API_KEY configured for direct fallback.")
        return FALLBACK_MESSAGE

    models_to_try = ["gemini-flash-latest", "gemini-flash-lite-latest", "gemini-3.8-flash"]
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 800,
            }
        }
        try:
            resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
            else:
                logger.warning(f"Gemini API ({model_name}) returned status {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"Error calling direct Gemini API ({model_name}): {e}")

    return FALLBACK_MESSAGE


def ask_college_assistant(
    student_question: str,
    retrieved_context: str,
    student_name: str = "",
    best_match: dict = None
) -> dict:
    """
    Run an agent inquiry with the student question and RAG context.
    Executes OpenClaw agent, falling back to direct API, and finally to verified RAG content.
    """
    get_agent_workspace()

    full_prompt = (
        f"{SYSTEM_INSTRUCTION}\n\n"
        f"=== COLLEGE KNOWLEDGE BASE CONTEXT ===\n"
        f"{retrieved_context}\n"
        f"=====================================\n\n"
        f"Student Name: {student_name or 'Student'}\n"
        f"Student Question: {student_question}\n\n"
        f"Assistant Answer:"
    )

    answer = None
    engine_used = "openclaw"

    # Attempt 1: OpenClaw CLI execution
    if os.path.exists(OPENCLAW_CMD):
        try:
            logger.info(f"Invoking OpenClaw agent for query: {student_question}")
            cmd = [
                OPENCLAW_CMD,
                "agent",
                "exec",
                full_prompt,
                "--cwd", str(WORKSPACE_DIR),
                "--model", "google/gemini-2.5-flash",
                "--json"
            ]
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=6,
                encoding="utf-8",
                errors="replace"
            )
            if process.returncode == 0 and process.stdout:
                try:
                    parsed = json.loads(process.stdout)
                    if isinstance(parsed, dict):
                        answer = parsed.get("reply") or parsed.get("output") or parsed.get("message")
                        if not answer and "turns" in parsed and len(parsed["turns"]) > 0:
                            answer = parsed["turns"][-1].get("reply")
                except json.JSONDecodeError:
                    answer = process.stdout.strip()

            if not answer and process.stdout:
                answer = process.stdout.strip()

        except subprocess.TimeoutExpired:
            logger.warning("OpenClaw command timed out; switching to direct Gemini engine.")
        except Exception as e:
            logger.warning(f"OpenClaw execution error ({e}); switching to direct Gemini engine.")

    # Attempt 2: Direct Gemini engine
    if not answer or not answer.strip():
        logger.info("Executing via Gemini Direct engine.")
        engine_used = "gemini_direct"
        gemini_reply = generate_with_gemini_direct(full_prompt)
        if gemini_reply and gemini_reply != FALLBACK_MESSAGE:
            answer = gemini_reply

    # Attempt 3: Authoritative Knowledge Base Match (if LLM is unreachable)
    if (not answer or not answer.strip() or answer == FALLBACK_MESSAGE) and best_match:
        if best_match.get("score", 0) >= 15:
            logger.info("Using authoritative Knowledge Base match directly.")
            engine_used = "knowledge_base_verified"
            answer = best_match["content"]

    # Final fallback if still empty
    if not answer or not answer.strip():
        answer = FALLBACK_MESSAGE

    clean_answer = answer.strip()

    # Determine status
    if FALLBACK_MESSAGE.lower() in clean_answer.lower():
        status = "FALLBACK"
        clean_answer = FALLBACK_MESSAGE
    else:
        status = "ANSWERED"

    return {
        "answer": clean_answer,
        "status": status,
        "engine": engine_used,
    }
