from pathlib import Path
from ...core import AppContainer
from .display import SetupDisplay


class SetupManager:
    def __init__(self, display: "SetupDisplay", app: "AppContainer"):
        self.display = display
        self.app = app

    def setup_project(self):
        """Main setup flow for the project"""
        env = self._handle_virtual_environment()
        self.app.django_manager.environment_service.state.active_venv_path = env[
            "virtual_env"
        ]

        if not env:
            return

        self._handle_requirements(env)

    def handle_requirements_setup(self, venv_path=None):
        """Coordinate the complete requirements setup flow"""
        requirements = (
            self.app.django_manager.requirements_service.find_or_extract_requirements(
                venv_path
            )
        )
        if not requirements:
            return False, "Failed to find or extract requirements"
        return self.app.django_manager.requirements_service.install_requirements_if_confirmed(
            requirements, venv_path
        )

    def _handle_virtual_environment(self):
        """Handle virtual environment setup flow"""
        venv = self.app.django_manager.environment_service.find_or_create_venv()

        if venv:
            return venv
        else:
            print("setup cancelled")
            return None

    def _handle_requirements(self, env_path):
        """Handle requirements setup flow"""
        success, message = self.handle_requirements_setup(env_path["virtual_env"])

        if not success:
            print(f"Setup cancelled: {message}")
