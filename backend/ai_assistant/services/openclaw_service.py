import os
import sys
import json
import logging
import shutil
import subprocess
import requests
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

FALLBACK_MESSAGE = "I don't have this information currently. Please contact the college office for the correct details."

AGENT_NAME = "college_assistant"
WORKSPACE_DIR = settings.BASE_DIR / "openclaw_college_agent"

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


def get_openclaw_executable() -> str:
    """Dynamically resolve OpenClaw CLI path across Windows/Linux/Mac."""
    configured = os.getenv("OPENCLAW_CMD")
    if configured and os.path.exists(configured):
        return configured

    # Check system PATH
    found = shutil.which("openclaw") or shutil.which("openclaw.cmd") or shutil.which("openclaw.CMD")
    if found:
        return found

    # Check user AppData roaming on Windows
    appdata = os.getenv("APPDATA")
    if appdata:
        cmd_path = Path(appdata) / "npm" / "openclaw.cmd"
        if cmd_path.exists():
            return str(cmd_path)

    # Check home directory fallback
    home_npm = Path.home() / "AppData" / "Roaming" / "npm" / "openclaw.cmd"
    if home_npm.exists():
        return str(home_npm)

    return ""


def get_gateway_info() -> dict:
    """Read OpenClaw Gateway configuration from ~/.openclaw/openclaw.json."""
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    default_info = {
        "url": os.getenv("OPENCLAW_GATEWAY_URL", "http://127.0.0.1:18789"),
        "token": os.getenv("OPENCLAW_GATEWAY_TOKEN", ""),
        "port": 18789,
        "is_configured": False
    }

    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            gateway = data.get("gateway", {})
            port = gateway.get("port", 18789)
            token = gateway.get("auth", {}).get("token", "")
            default_info["port"] = port
            default_info["url"] = f"http://127.0.0.1:{port}"
            default_info["token"] = token or default_info["token"]
            default_info["is_configured"] = True
        except Exception as e:
            logger.warning(f"Could not parse openclaw.json: {e}")

    return default_info


def inspect_openclaw_status() -> dict:
    """Health check for OpenClaw connection (CLI, Gateway, Workspace, Agent)."""
    executable = get_openclaw_executable()
    gateway = get_gateway_info()
    workspace = get_agent_workspace()

    gateway_online = False
    gateway_ping_ms = 0
    try:
        import time
        start = time.time()
        resp = requests.get(f"{gateway['url']}/", timeout=1.5)
        gateway_ping_ms = round((time.time() - start) * 1000)
        gateway_online = resp.status_code in [200, 401, 403, 404]
    except Exception:
        gateway_online = False

    cli_version = "Not found"
    if executable:
        try:
            res = subprocess.run([executable, "--version"], capture_output=True, text=True, timeout=3)
            if res.returncode == 0:
                cli_version = res.stdout.strip()
        except Exception:
            cli_version = "Installed (CLI probe timeout)"

    return {
        "connected": bool(executable or gateway_online),
        "cli_path": executable or "Not in PATH",
        "cli_version": cli_version,
        "gateway_url": gateway["url"],
        "gateway_online": gateway_online,
        "gateway_ping_ms": gateway_ping_ms if gateway_online else None,
        "agent_name": AGENT_NAME,
        "workspace_path": str(workspace),
        "knowledge_catalog_exists": (workspace / "knowledge" / "COLLEGE_CATALOG.md").exists(),
        "faqs_exists": (workspace / "knowledge" / "FAQS.md").exists(),
    }


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


def generate_with_openclaw_gateway(prompt: str) -> str:
    """Query OpenClaw through its local HTTP Gateway (/v1/chat/completions)."""
    gateway = get_gateway_info()
    if not gateway["url"]:
        return ""

    headers = {"Content-Type": "application/json"}
    if gateway["token"]:
        headers["Authorization"] = f"Bearer {gateway['token']}"

    payload = {
        "model": f"openclaw/{AGENT_NAME}",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
    }

    try:
        resp = requests.post(f"{gateway['url']}/v1/chat/completions", json=payload, headers=headers, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()
    except Exception as e:
        logger.debug(f"OpenClaw gateway query bypassed/failed: {e}")

    return ""


def generate_with_gemini_direct(prompt: str) -> str:
    """Direct Google Gemini API fallback using GEMINI_API_KEY / GOOGLE_API_KEY."""
    api_key = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
    if not api_key:
        return FALLBACK_MESSAGE

    models_to_try = ["gemini-flash-latest", "gemini-flash-lite-latest", "gemini-3.8-flash"]
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 800,
            }
        }
        try:
            resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
        except Exception:
            continue

    return FALLBACK_MESSAGE


def ask_college_assistant(
    student_question: str,
    retrieved_context: str,
    student_name: str = "",
    best_match: dict = None
) -> dict:
    """
    Run an agent inquiry with the student question and RAG context.
    Executes OpenClaw Gateway/Agent, falling back to direct API, and finally to verified RAG content.
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
    engine_used = "openclaw_gateway"

    # 1. Try local OpenClaw Gateway (HTTP)
    gateway_reply = generate_with_openclaw_gateway(full_prompt)
    if gateway_reply:
        answer = gateway_reply

    # 2. Try OpenClaw CLI
    if not answer or not answer.strip():
        executable = get_openclaw_executable()
        if executable and os.path.exists(executable):
            try:
                engine_used = "openclaw_cli"
                cmd = [
                    executable,
                    "agent",
                    "--agent", AGENT_NAME,
                    "--message", full_prompt,
                    "--json"
                ]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=8, encoding="utf-8", errors="replace")
                if proc.returncode == 0 and proc.stdout:
                    try:
                        parsed = json.loads(proc.stdout)
                        if isinstance(parsed, dict):
                            answer = parsed.get("reply") or parsed.get("output") or parsed.get("message")
                    except Exception:
                        answer = proc.stdout.strip()
            except Exception as e:
                logger.debug(f"OpenClaw CLI execution notice: {e}")

    # 3. Direct Gemini LLM fallback
    if not answer or not answer.strip() or answer == FALLBACK_MESSAGE:
        engine_used = "gemini_direct"
        gemini_reply = generate_with_gemini_direct(full_prompt)
        if gemini_reply and gemini_reply != FALLBACK_MESSAGE:
            answer = gemini_reply

    # 4. Verified RAG Match fallback
    if (not answer or not answer.strip() or answer == FALLBACK_MESSAGE) and best_match:
        if best_match.get("score", 0) >= 15:
            engine_used = "knowledge_base_verified"
            answer = best_match["content"]

    if not answer or not answer.strip():
        answer = FALLBACK_MESSAGE

    clean_answer = answer.strip()
    status = "FALLBACK" if FALLBACK_MESSAGE.lower() in clean_answer.lower() else "ANSWERED"

    return {
        "answer": clean_answer,
        "status": status,
        "engine": engine_used,
    }
