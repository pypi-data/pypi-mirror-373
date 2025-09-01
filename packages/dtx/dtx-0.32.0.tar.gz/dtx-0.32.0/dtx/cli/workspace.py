import os
import shutil

from dtx.core import logging

from .env_manager import (
    EnvLoader,
    EnvTemplateManager,
)


class WorkspaceManager:
    def __init__(self, base_dir, template_dir, required_env_vars):
        self.logger = logging.getLogger("WorkspaceManager")
        self.base_dir = base_dir
        self.templates_dir = template_dir
        self.env_file_manager = EnvTemplateManager(base_dir=self.base_dir)
        self.env_loader = EnvLoader(env_path=self.env_file_manager.env_path)
        self.required_env_vars = required_env_vars

    def prepare(self):
        """Ensure workspace and environment are ready."""
        self._ensure_directories()
        self.env_file_manager.ensure_env_file()
        self.env_loader.load_env()
        self.env_loader.configure()
        # self.env_loader.validate(self.required_env_vars)

    def _ensure_directories(self):
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "tmp"), exist_ok=True)

    def handle_templates(self, args):
        repo_url = "https://github.com/detoxio-ai/dtx_templates.git"

        if args.templates_command == "update":
            if os.path.exists(self.templates_dir):
                self.logger.info("Removing old templates...")
                shutil.rmtree(self.templates_dir)

            self.logger.info(f"Cloning templates from {repo_url}...")
            os.system(f"git clone {repo_url} {self.templates_dir}")
            print(f"✅ Templates updated at: {self.templates_dir}")

        elif args.templates_command == "list":
            scope_path = os.path.join(self.templates_dir, "templates/scope")
            plan_path = os.path.join(self.templates_dir, "templates/plan")

            print("\n📂 Scope Templates:")
            if os.path.isdir(scope_path):
                for file in sorted(os.listdir(scope_path)):
                    print(f"  - {file}")
            else:
                print("  (none found)")

            print("\n📂 Plan Templates:")
            if os.path.isdir(plan_path):
                for file in sorted(os.listdir(plan_path)):
                    print(f"  - {file}")
            else:
                print("  (none found)")
