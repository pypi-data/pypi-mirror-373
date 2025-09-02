from typing import Tuple, List, Optional

from .os_manager.command_runner import CommandResult
from ..managers import OSManager, ConsoleManager, EnvManager


class DatabaseManager:
    def __init__(
        self,
        os_manager: OSManager,
        console_manager: Optional[ConsoleManager] = None,
        env_manager: Optional[EnvManager] = None,
    ):
        self.os_manager = os_manager
        self.console_manager = console_manager
        self.env_manager = env_manager
        self._superuser = "postgres"
        self._superuser_password = ""
        self.host = ""
        self.database = "postgres"
        self.username = ""
        self._db_name = ""
        self.dependencies = ["psycopg2-binary"]

    # Property getters/setters
    @property
    def superuser(self) -> str:
        return self._superuser

    @superuser.setter
    def superuser(self, value: str):
        self._superuser = value

    @property
    def superuser_password(self) -> str:
        return self._superuser_password

    @superuser_password.setter
    def superuser_password(self, value: str):
        self._superuser_password = value

    @property
    def db_name(self) -> str:
        return self._db_name

    @db_name.setter
    def db_name(self, value: str):
        self._db_name = value

    # Core database connection methods
    def _get_admin_connection(self):
        """Get connection with superuser privileges using peer authentication."""
        # Ensure dependencies are installed
        if not self.ensure_dependencies():
            raise ImportError("Database dependencies not available")

        # Dynamic import to avoid startup errors if package is missing
        import psycopg2

        return psycopg2.connect(
            dbname=self.database,
            user=self.superuser,
            host="",  # Empty host forces Unix domain socket connection
        )

    def set_database_user(self, username):
        self.username = username

    def _get_connection(self):
        # Ensure dependencies are installed
        if not self.ensure_dependencies():
            raise ImportError("Database dependencies not available")

        # Dynamic import to avoid startup errors if package is missing
        import psycopg2

        return psycopg2.connect(
            dbname=self.database,
            user=self.username,
            host=self.host,
        )

    def login_user(self, username):
        self.set_database_user(username)
        try:
            # Ensure dependencies are installed
            if not self.ensure_dependencies():
                return False, "Database dependencies not available"

            # Dynamic import to avoid startup errors if package is missing
            import psycopg2

            conn = self._get_connection()
            conn.close()
            return True, "Login successful"
        except psycopg2.Error as e:
            return False, f"Login failed: {str(e)}"
        except ImportError as e:
            return False, f"Database dependency error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error during login: {str(e)}"

    def execute_admin_command(self, command: str, params=None) -> Tuple[bool, str]:
        """Execute a command with superuser privileges."""
        try:
            # Run the command as the postgres system user
            cmd = f'sudo -u postgres psql -c "{command}"'
            success = self.os_manager.run_command(cmd)
            if not success.success:
                return False, f"Command failed: {success.stderr}"
            return True, "Command executed successfully"
        except Exception as e:
            return False, f"Database error: {str(e)}"

    # Database operations
    def create_database(self, db_name: str) -> Tuple[bool, str]:
        """Create a new database."""
        self.db_name = db_name.lower()
        return self.execute_admin_command(f"CREATE DATABASE {db_name};")

    def create_user(self, username: str) -> Tuple[bool, str]:
        """Create a new database user."""
        return self.execute_admin_command(f"CREATE USER {username};")

    # Installation and configuration methods
    def install_postgres(self):
        """
        Install PostgreSQL with progress updates.

        Yields:
            Tuple[str, bool, str]: (step_name, success, message)
        """

        # Install packages
        success, message = self.install_postgres_packages()
        if not success:
            yield "Package Installation", False, message
            return
        yield "Package Installation", True, "Packages installed successfully"

        # Configure service
        success, message = self.configure_postgres_service()
        if not success:
            yield "Service Configuration", False, message
            return
        yield "Service Configuration", True, "Service configured successfully"

        # Configure user
        success, message = self.configure_postgres_user()
        if not success:
            yield "User Configuration", False, message
            return
        yield "User Configuration", True, "User configured successfully"

        # Verify installation
        is_installed, location = self.check_postgres_installation()
        if not is_installed:
            yield "Installation Verification", False, "PostgreSQL installation could not be verified"
            return

        is_running = self.check_postgres_status()
        if not is_running:
            yield "Service Verification", False, "PostgreSQL service is not running"
            return

        yield "Installation Complete", True, f"PostgreSQL successfully installed at {location}"

    def install_postgres_packages(self):
        """
        Install PostgreSQL packages and dependencies.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        package_names = [
            "postgresql",
            "postgresql-contrib",
            "postgresql-client",
            "libpq-dev",
        ]

        for package in package_names:
            success = self.os_manager.install_package(package)
            if not success:
                return False, f"Failed to install {package}: {success.stderr}"

        return True, "PostgreSQL packages installed successfully"

    def configure_postgres_service(self):
        """
        Enable and start the PostgreSQL service.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        # Enable service
        success = self.os_manager.enable_service("postgresql")
        if not success.success:
            return False, f"Failed to enable PostgreSQL service: {success.stderr}"

        # Start service
        success = self.os_manager.start_service("postgresql")
        if not success.success:
            return False, f"Failed to start PostgreSQL service: {success.stderr}"

        return True, "PostgreSQL service started successfully"

    def configure_postgres_user(self):
        """
        Configure PostgreSQL user and initial database.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Create default user if doesn't exist
            if not self.os_manager.user_exists("postgres"):
                success = self.os_manager.run_command(
                    "sudo -u postgres createuser --superuser $USER"
                )
                if not success.success:
                    return False, f"Failed to create PostgreSQL user: {success.stderr}"

            return True, "PostgreSQL user configured successfully"
        except Exception as e:
            return False, f"Failed to configure PostgreSQL user: {str(e)}"

    # Status check methods

    def check_postgres_installation(self) -> Tuple[bool, str]:
        """
        Check if PostgreSQL is properly installed by verifying the client component.

        Returns:
            Tuple[bool, str]: (is_installed, message)
        """
        is_client_installed = self.os_manager._manager.check_package_installed("psql")

        if not is_client_installed:
            return False, "PostgreSQL client (psql) not found"

        return True, "PostgreSQL installed"

    def check_postgres_status(self) -> bool:
        is_active = self.os_manager._manager.check_service_status("postgresql")
        return is_active.success

    def get_all_databases(self) -> Tuple[bool, list | str]:
        """
        Get a list of all PostgreSQL databases, excluding system databases.

        Returns:
            Tuple[bool, Union[list, str]]: (success, list of databases or error message)
        """
        try:
            # Use psql to list databases
            cmd = "sudo -u postgres psql -t -c \"SELECT datname FROM pg_database WHERE datname NOT IN ('template0', 'template1', 'postgres');\""
            success = self.os_manager.run_command(cmd)

            if not success.success:
                return False, f"Failed to get databases: {success.stderr}"

            # Process the output - strip whitespace and empty lines
            databases = [db.strip() for db in success.stdout.split("\n") if db.strip()]
            return True, databases

        except Exception as e:
            return False, f"Error getting databases: {str(e)}"

    # Dependency management methods
    def get_dependencies(self) -> List[str]:
        """Returns the list of dependencies required by the database manager"""
        return self.dependencies

    def check_dependency_installed(self, dependency: str) -> bool:
        """Checks if a specific dependency is installed"""
        if dependency == "psycopg2-binary":
            return self.os_manager.check_pip_package_installed(
                "psycopg2"
            ).success or self.os_manager.check_pip_package_installed("psycopg2-binary").success
        return False

    def install_dependency(self, dependency: str) -> CommandResult:
        """Install a specific dependency."""
        if dependency not in self.dependencies:
            return CommandResult(
                success=False,
                stdout="",
                stderr=f"{dependency} is not a recognized dependency",
                exit_code=1,
            )

        if dependency == "psycopg2-binary":
            # First ensure libpq-dev is installed (needed for psycopg2)
            libpq_res = self.os_manager.install_package("libpq-dev")
            if not libpq_res.success and self.console_manager:
                self.console_manager.print_step_failure(
                    "Dependencies", libpq_res.stderr
                )

            # Install with pip
            return self.os_manager.install_pip_package("psycopg2-binary")

        return CommandResult(
            success=False,
            stdout="",
            stderr=f"No installation method for {dependency}",
            exit_code=1,
        )

    def verify_dependencies(self) -> List[Tuple[str, bool, str]]:
        """Verifies all dependencies and returns results"""
        results = []
        for dependency in self.dependencies:
            is_installed = self.check_dependency_installed(dependency)
            status_msg = (
                f"{dependency} is {'installed' if is_installed else 'not installed'}"
            )
            results.append((dependency, is_installed, status_msg))
        return results

    def ensure_dependencies(self) -> bool:
        """
        Ensures all database dependencies are installed, prompting for installation if needed.
        Uses the centralized EnvManager for Python packages.

        Returns:
            bool: True if all dependencies are available (or were successfully installed), False otherwise
        """
        # First ensure system dependencies (libpq-dev is needed for psycopg2)
        success = self.os_manager.install_package("libpq-dev")
        if not success.success and self.console_manager:
            self.console_manager.print_step_failure("System Dependency", success.stderr)

        # Use the env_manager to handle Python package dependencies if available
        if self.env_manager:
            success, message, _ = self.env_manager.ensure_dependencies(
                None,  # Will use active venv or system Python
                self.dependencies,
                "Install required database dependencies?",
            )
            return success

        # Fallback to directly checking packages if env_manager not provided
        return all(
            self.os_manager.check_pip_package_installed(pkg).success
            for pkg in self.dependencies
        )
