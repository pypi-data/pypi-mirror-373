from ....console_manager import ConsoleManager


class SecretKeyHandlerDisplay:

    def __init__(self, console_manager: "ConsoleManager"):
        self.console_manager = console_manager

    def progress_generate_secret_key(self):
        self.console_manager.print_progress("Generating secret key")

    def success_generate_secret_key(self, secret_key):
        self.console_manager.print_success(f"Secret key generated: {secret_key}")

    def progress_set_secret_key(self, secret_key, old_key):
        self.console_manager.print_progress(
            f"Replacing old key {old_key} with {secret_key}"
        )

    def success_set_secret_key(self):
        self.console_manager.print_step_progress("Secret key", "set successfully")
