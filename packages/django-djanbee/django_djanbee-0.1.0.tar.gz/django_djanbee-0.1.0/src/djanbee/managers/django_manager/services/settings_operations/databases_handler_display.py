from ....console_manager import ConsoleManager
from .....widgets.text_input import TextInputWidget
from .....widgets.list_selector import ListSelector
from .....widgets.question_selector import QuestionSelector


class DatabasesHandlerDisplay:

    def __init__(self, console_manager: "ConsoleManager"):
        self.console_manager = console_manager

    def prompt_postgresql_edit(self, database):
        # Create a list of tuples with field names and current values
        # Convert all values to strings to ensure .strip() will work
        fields = [
            ("ENGINE", str(database.get("ENGINE", "django.db.backends.postgresql"))),
            ("NAME", str(database.get("NAME", ""))),
            ("USER", str(database.get("USER", ""))),
            ("PASSWORD", str(database.get("PASSWORD", ""))),
            ("HOST", str(database.get("HOST", "localhost"))),
            ("PORT", str(database.get("PORT", "5432"))),
            ("CONN_MAX_AGE", str(database.get("CONN_MAX_AGE", "600"))),
        ]

        # Create the input widget
        input_widget = TextInputWidget(
            "Configure PostgreSQL database:",
            fields,
            self.console_manager,
        )

        # Get the results from the widget
        results = input_widget.get_result()
        if results is None:
            return None

        # Validate required fields
        required_fields = ["ENGINE", "NAME"]
        for field in required_fields:
            if not results.get(field, "").strip():
                self.console_manager.print_warning_critical(f"Please fill in {field}")
                return self.prompt_postgresql_edit(database)

        # Build the updated database configuration dictionary
        updated_database = {
            "ENGINE": results.get("ENGINE").strip(),
            "NAME": results.get("NAME").strip(),
        }

        # Add optional fields if they have values
        for field in ["USER", "PASSWORD", "HOST", "PORT", "CONN_MAX_AGE"]:
            value = results.get(field, "").strip()
            if value:
                # For PORT and CONN_MAX_AGE, try to convert to integer
                if field in ["PORT", "CONN_MAX_AGE"]:
                    try:
                        updated_database[field] = int(value)
                    except ValueError:
                        # Keep as string if not a valid integer
                        updated_database[field] = value
                else:
                    updated_database[field] = value

        # Add SSL options if host is not localhost
        if updated_database.get("HOST") and updated_database.get("HOST") != "localhost":
            ssl_option = self.prompt_for_ssl_mode()
            if ssl_option:
                updated_database["OPTIONS"] = {"sslmode": ssl_option}

        return updated_database

    def prompt_for_ssl_mode(self):
        """Prompt user to select an SSL mode for PostgreSQL connection"""
        ssl_modes = [
            "disable",
            "allow",
            "prefer",
            "require",
            "verify-ca",
            "verify-full",
        ]

        result = ListSelector(
            "Select SSL mode for database connection (if not sure leave allow):",
            ssl_modes,
            self.console_manager,
        )

        return result.select()

    def success_database_updated(self):
        self.console_manager.print_success("Database successfully updated")

    def print_lookup_database_dependencies(self):
        self.console_manager.print_lookup("Looking for database dependencies")

    def prompt_install_database_dependencies(self, dependencies):
        selector = QuestionSelector(
            f"Missing dependencies: {dependencies} \n Do you wish to install",
            self.console_manager,
        )
        return selector.select()

    def print_progress_database_dependencies_install(self):
        self.console_manager.print_progress("Installing dependencies")

    def print_database_dependencies_present(self):
        self.console_manager.print_step_progress(
            "Database dependencies", "All dependencies present"
        )
