import json
import logging
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from ai_assistant.services.openclaw_service import get_agent_workspace, WORKSPACE_DIR, FALLBACK_MESSAGE
from ai_assistant.services.rag_service import sync_knowledge_to_workspace

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Initializes and registers the dedicated OpenClaw College Assistant agent'

    def handle(self, *args, **options):
        self.stdout.write("Configuring dedicated OpenClaw College Assistant agent...")

        workspace_dir = get_agent_workspace()
        self.stdout.write(f"Workspace directory initialized at: {workspace_dir}")

        # 1. Sync Knowledge Base to workspace
        sync_knowledge_to_workspace(workspace_dir)
        self.stdout.write("Knowledge files exported to workspace.")

        # 2. Register agent in ~/.openclaw/openclaw.json if present
        openclaw_config_path = Path.home() / ".openclaw" / "openclaw.json"
        if openclaw_config_path.exists():
            try:
                with open(openclaw_config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)

                if "agents" not in config:
                    config["agents"] = {"entries": {}}
                if "entries" not in config["agents"]:
                    config["agents"]["entries"] = {}

                agent_dir = Path.home() / ".openclaw" / "agents" / "college_assistant" / "agent"
                agent_dir.mkdir(parents=True, exist_ok=True)

                config["agents"]["entries"]["college_assistant"] = {
                    "workspace": str(workspace_dir),
                    "agentDir": str(agent_dir),
                    "model": {
                        "primary": "google/gemini-2.5-flash"
                    }
                }

                with open(openclaw_config_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2)

                self.stdout.write(self.style.SUCCESS(
                    "Registered 'college_assistant' in ~/.openclaw/openclaw.json successfully!"
                ))
            except Exception as e:
                self.stdout.write(self.style.WARNING(
                    f"Notice: Could not modify openclaw.json ({e}). Isolated workspace mode will be used."
                ))
        else:
            self.stdout.write("OpenClaw config not found in standard location, using local workspace.")

        self.stdout.write(self.style.SUCCESS(
            "Dedicated OpenClaw College Assistant setup completed successfully!"
        ))
