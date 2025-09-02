from pathlib import Path


class DjangoManagerState:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._current_project_path = None
        self._active_venv_path = None
        self._current_requirements_path = None
        self._settings_path = None

    @property
    def current_project_path(self):
        """Get the current project path"""
        return self._current_project_path

    @current_project_path.setter
    def current_project_path(self, value):
        """Set the current project path with validation"""
        # You could add validation here
        if value is not None and not isinstance(value, Path):
            value = Path(value)
        self._current_project_path = value

    @property
    def active_venv_path(self):
        """Get the active virtual environment path"""
        return self._active_venv_path

    @active_venv_path.setter
    def active_venv_path(self, value):
        """Set the active virtual environment path with validation"""
        if value is not None and not isinstance(value, Path):
            value = Path(value)
        self._active_venv_path = value

    @property
    def current_requirements_path(self):
        """Get the current requirements path"""
        return self._current_requirements_path

    @current_requirements_path.setter
    def current_requirements_path(self, value):
        """Set the current requirements path with validation"""
        if value is not None and not isinstance(value, Path):
            value = Path(value)
        self._current_requirements_path = value

    @property
    def settings_path(self):
        """Get the Django settings file path"""
        return self._settings_path

    @settings_path.setter
    def settings_path(self, value):
        """Set the Django settings file path with validation"""
        if value is not None and not isinstance(value, Path):
            value = Path(value)
        self._settings_path = value
