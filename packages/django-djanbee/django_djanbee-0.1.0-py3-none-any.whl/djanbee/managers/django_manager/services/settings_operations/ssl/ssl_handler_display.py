from .....console_manager import ConsoleManager
from ......widgets.checkbox_selector import CheckboxSelector
from ......widgets.text_input import TextInputWidget
from ......widgets.list_selector import ListSelector
class SslHandlerDisplay:
    def __init__(self, console_manager: ConsoleManager):
        self.console_manager = console_manager
        
    def prompt_configure_menu(self, current_settings):
        options = [
            "SECURE_SSL_REDIRECT",
            "SESSION_COOKIE_SECURE",
            "CSRF_COOKIE_SECURE",
            "SECURE_HSTS_SECONDS",
            "SECURE_HSTS_INCLUDE_SUBDOMAINS",
            "SECURE_PROXY_SSL_HEADER",
        ]

        result = CheckboxSelector(
            "Select ssl settings to configure:", options, self.console_manager, current_settings
        )
        return result.select()
    
    def cancelled_operation(self):
        print("Operation cancelled")
    
    def info_ssl_config(self):
        self.console_manager.print_info("No SSL settings needed to be changed")
    
    def success_update_bool_setting(self, setting, value):
        self.console_manager.print_step_progress(setting, f"Set to {value}")
    
    def success_ssl_config(self):
        self.console_manager.print_success("SSL setup finished successfully")

    def input_hsts_seconds(self, current_seconds):
        """
        Prompt the user to enter HSTS seconds value with validation
        
        Args:
            current_seconds: Current value of SECURE_HSTS_SECONDS
            
        Returns:
            int: Validated seconds value, or None if cancelled
        """
        if current_seconds is None:
            current_seconds = ""
        fields = [("SECURE_HSTS_SECONDS", str(current_seconds))]
        input_widget = TextInputWidget(
            "Set the SECURE_HSTS_SECONDS:", fields, self.console_manager
        )
        results = input_widget.get_result()
        if results is None:
            return None

        seconds_str = results.get("SECURE_HSTS_SECONDS", "").strip()

        if not seconds_str:
            self.console_manager.print_warning_critical("Please enter a value for HSTS seconds")
            return self.input_hsts_seconds(current_seconds)

        try:
            seconds = int(seconds_str)
            if seconds < 0:
                self.console_manager.print_warning_critical("HSTS seconds must be a positive number")
                return self.input_hsts_seconds(current_seconds)
            return seconds
        except ValueError:
            self.console_manager.print_warning_critical("HSTS seconds must be a valid integer")
            return self.input_hsts_seconds(current_seconds)
        
    def success_update_hsts_seconds(self, value):
        self.console_manager.print_step_progress("SECURE_HSTS_SECONDS", f"Set value to {value}")
    
    def success_disable_hsts_seconds(self):
        self.console_manager.print_step_progress("SECURE_HSTS_SECONDS", "Disabled")
    
    def success_update_proxy_header(self, proxy_type):
        self.console_manager.print_step_progress("SECURE_PROXY_SSL_HEADER", f"Set to {proxy_type}")
    
    def success_disable_proxy_header(self):
        self.console_manager.print_step_progress("SECURE_PROXY_SSL_HEADER", "Disabled")
    
    def prompt_select_proxy_header(self):
        """
        Prompt the user to select which proxy header configuration to use.
        
        Returns:
            tuple: Selected header configuration tuple, or None if cancelled
        """
        selector = ListSelector(
            "Select proxy header configuration:",
            [
                "HTTP_X_FORWARDED_PROTO, https (most common, works with Nginx, AWS ELB)",
                "HTTP_X_FORWARDED_SCHEME, https (some proxies)",
                "HTTP_X_SCHEME, https (less common)",
                "HTTP_FRONT_END_HTTPS, on (Microsoft IIS/ARR)"
            ],
            self.console_manager,
        )
        
        selected = selector.select()
        if selected is None:
            return None
        
        # Map the selection to the appropriate tuple
        if selected == "HTTP_X_FORWARDED_PROTO, https (most common, works with Nginx, AWS ELB)":
            return ('HTTP_X_FORWARDED_PROTO', 'https')
        elif selected == "HTTP_X_FORWARDED_SCHEME, https (some proxies)":
            return ('HTTP_X_FORWARDED_SCHEME', 'https')
        elif selected == "HTTP_X_SCHEME, https (less common)":
            return ('HTTP_X_SCHEME', 'https')
        elif selected == "HTTP_FRONT_END_HTTPS, on (Microsoft IIS/ARR)":
            return ('HTTP_FRONT_END_HTTPS', 'on')
        
        return None
