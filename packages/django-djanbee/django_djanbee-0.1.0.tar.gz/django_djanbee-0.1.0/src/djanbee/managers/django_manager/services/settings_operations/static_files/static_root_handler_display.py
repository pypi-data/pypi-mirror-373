from .....console_manager import ConsoleManager
from ......widgets.list_selector import ListSelector
from ......widgets.question_selector import QuestionSelector
from ......widgets.text_input import TextInputWidget


class StaticRootHandlerDisplay:

    def __init__(self, console_manager: "ConsoleManager"):
        self.console_manager = console_manager

    def prompt_static_files_solution(self):

        selector = ListSelector(
            "Select static file handling solution:",
            ["Whitenoise", "Nginx"],
            self.console_manager,
        )
        return selector.select()

    def prompt_install_whitenoise(self):
        selector = QuestionSelector(
            "Whitenoise not installed \n Do you wish to install it now:",
            self.console_manager,
        )
        return selector.select()

    def print_progress_whitenoise(self):
        self.console_manager.print_progress("Setting whitenoise in middleware")

    def success_progress_whitenoise(self):
        self.console_manager.print_step_progress(
            "Middleware", "Whitenoise added to middleware"
        )

    def print_progress_static_url(self):
        self.console_manager.print_progress("Setting static url")

    def success_progress_static_url(self, url = "/static/"):
        self.console_manager.print_step_progress(
            "STATIC_URL", f"Static url set to {url}"
        )

    def print_progress_static_root(self):
        self.console_manager.print_progress("Setting static root")

    def success_progress_static_root(self):
        self.console_manager.print_step_progress(
            "STATIC_ROOT", "os.path.join(BASE_DIR, 'staticfiles')"
        )

    def print_progress_static_root_add_os(self):
        self.console_manager.print_progress("OS library missing, ading library")

    def print_progress_static_file_dirs_create(self):
        self.console_manager.print_progress("Creating STATICFILE_DIRS setting")

    def success_progress_static_file_dirs_add(self, name):
        self.console_manager.print_step_progress("STATICFILE_DIRS", f"{name} added")

    def progress_staticfiles_storage_add(self):
        self.console_manager.print_progress("Adding whitenoise to staticfile storage")

    def success_staticfiles_storage_add(self):
        self.console_manager.print_step_progress(
            "STATICFILES_STORAGE", "Whitenoise added"
        )
    
    def error_unsupported_handler(self, result):
        self.console_manager.print_error(f"UNSUPPORTED HANDLER: {result}")
        
    def success_static_files_setup(self, result):
        self.console_manager.print_step_progress("STATICFILES", result)
        self.console_manager.print_success("Staticfiles setup finished")
        
    def error_static_files_setup(self, result):
        self.console_manager.print_error(result)
    
    def input_static_url(self, static_url):
        fields = [("STATIC_URL", static_url)]
        input_widget = TextInputWidget(
            "Set the STATIC_URL:", fields, self.console_manager
        )
        results = input_widget.get_result()
        if results is None:
            return None

        url = results.get("STATIC_URL", "").strip()

        if not len(url):
            self.console_manager.print_warning_critical("Please fill in hostname")
            return self.input_static_url(static_url)

        return url

    def print_progress_media_root(self):
        self.console_manager.print_progress("Setting MEDIA_ROOT")
    
    def print_progress_media_url(self):
        self.console_manager.print_progress("Setting MEDIA_URL")
    
    def print_progress_media_root_add_os(self):
        self.console_manager.print_progress("Importing os library for MEDIA_ROOT")
    
    def success_progress_media_settings(self, media_url, media_root):
        self.console_manager.print_step_progress("MEDIA_URL", media_url)
        self.console_manager.print_step_progress("MEDIA_ROOT", media_root)



