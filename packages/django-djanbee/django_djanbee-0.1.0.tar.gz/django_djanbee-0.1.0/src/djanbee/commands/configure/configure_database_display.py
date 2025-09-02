from ...managers import ConsoleManager
from ...widgets.question_selector import QuestionSelector
from ...widgets.list_selector import ListSelector


class ConfigureDatabaseDisplay:
    def __init__(self, console_manager: "ConsoleManager"):
        self.console_manager = console_manager

    def show_lookup_database(self):
        self.console_manager.print_lookup("Searching for database installation")

    def success_database_installed(self, database_location: str):
        self.console_manager.print_success(
            f"Database installation found at {database_location}"
        )

    def error_database_installed(self):
        self.console_manager.print_error(f"Database installation not found")

    def prompt_install_database(self):
        selector = QuestionSelector(
            "Do you wish to install a database (postgresql)", self.console_manager
        )
        return selector.select()
    
    def prompt_set_default_config(self):
        selector = QuestionSelector(
            "Do you wish to generate database config for a local postgresql database",
            self.console_manager,
            warning="Peer connection only!!! (for now)",
        )
        return selector.select()

    def prompt_enable_database(self):
        selector = QuestionSelector(
            "Do you wish to start database related services", self.console_manager
        )
        return selector.select()

    def print_installation_progress(self, step_name, message):
        self.console_manager.print_step_progress(step_name, message)

    def print_installation_failure(self, step_name, message):
        self.console_manager.print_step_failure(step_name, message)

    def error_database_running(self):
        self.console_manager.print_error("Database service not running")

    def success_database_running(self):
        self.console_manager.print_success("Database service enabled and running")

    def prompt_database_create_or_connect(self):
        selector = QuestionSelector(
            "Would you like to create a new database or connect an existing one?",
            self.console_manager,
            "create",
            "connect",
        )
        return selector.select()

    def prompt_user_create_or_login(self, is_admin):
        warning = ""
        if is_admin:
            warning = "PostgreSQL peer authentication requires your database user to match your system username - running as root is not recommended and may cause authentication issues."
        selector = QuestionSelector(
            "Would you like to create a new database user or login with an existing one? (Using peer connection)",
            self.console_manager,
            "login",
            "create",
            warning=warning,
        )
        return selector.select()

    def success_create_user(self, user):
        self.console_manager.print_step_progress(
            "Database", f"Successfully created user {user}"
        )

    def error_create_user(self, e):
        self.console_manager.print_step_failure(
            "Database", f"Failed to create user: {str(e)}"
        )

    def success_login_user(self, user):
        self.console_manager.print_success(f"Successfully logged in user {user}")

    def error_login_user(self, e):
        self.console_manager.print_step_failure(
            "Database", f"Failed to login user: {str(e)}"
        )

    def input_database_name(self) -> str:
        """Get database name input from user with styled prompt"""
        self.console_manager.print_package("Enter database name: ")
        try:
            db_name = input()
            if db_name.strip():
                # Basic validation for PostgreSQL database names
                if db_name.isalnum() or "_" in db_name:
                    return (
                        db_name.lower()
                    )  # PostgreSQL converts names to lowercase anyway
                else:
                    self.console_manager.print_step_failure(
                        "Database",
                        "Database name can only contain letters, numbers, and underscores",
                    )
                    return self.input_database_name()
            else:
                self.console_manager.print_step_failure(
                    "Database", "Database name cannot be empty"
                )
                return self.input_database_name()
        except Exception as e:
            self.console_manager.print_error(str(e))
            return self.input_database_name()

    def prompt_select_database(self, databases):
        if not databases:
            return None

        choices = [p for p in databases]

        self.console_manager.console.print("\nDid you mean one of these Databases?")
        selector = ListSelector("Select a Database", choices, self.console_manager)
        return selector.select()

    def print_progress_database(self, db_name):
        self.console_manager.print_input(f"Set database as {db_name}")

    def progress_install_database(self):
        self.console_manager.print_progress(f"Installing database")

    def show_permissions_setup(self, username):
        """Display information about setting up permissions."""
        self.console_manager.print_info(f"Setting up database permissions for {username}")

    def show_permissions_success(self):
        """Display success message for permissions setup."""
        self.console_manager.print_success("Database permissions configured successfully")

    def show_permissions_error(self):
        """Display error message for permissions setup."""
        self.console_manager.print_error("Failed to configure database permissions")

    def show_config_update(self):
        """Display information about updating database config."""
        self.console_manager.print_info("Updating database configuration for peer authentication")

    def show_config_success(self):
        """Display success message for config update."""
        self.console_manager.print_success("Database configuration updated successfully")

    def show_config_error(self):
        """Display error message for config update."""
        self.console_manager.print_error("Failed to update database configuration")