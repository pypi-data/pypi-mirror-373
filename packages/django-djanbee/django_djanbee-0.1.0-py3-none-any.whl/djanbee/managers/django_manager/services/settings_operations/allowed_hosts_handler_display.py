from ....console_manager import ConsoleManager
from .....widgets.text_input import TextInputWidget
from .....widgets.create_delete_chekbox_selector import CreateDeleteCheckboxSelector


class AllowedHostsHandlerDisplay:

    def __init__(self, console_manager: "ConsoleManager"):
        self.console_manager = console_manager

    def prompt_allowed_hosts_manager(self, hosts):
        result = CreateDeleteCheckboxSelector(
            "Delete hosts or create a new host", hosts, self.console_manager
        )

        return result.select()

    def prompt_allowed_hosts_input(self, host=""):
        fields = [("Hostname", host)]
        input_widget = TextInputWidget(
            "Add an allowed host:", fields, self.console_manager
        )
        results = input_widget.get_result()
        if results is None:
            return None

        hostname = results.get("Hostname", "").strip()

        if not len(hostname):
            self.console_manager.print_warning_critical("Please fill in hostname")
            return self.prompt_allowed_hosts_input(host)

        return hostname

    def warning_empty_hosts(self):
        self.console_manager.print_warning_critical(
            "No hosts set in ALLOWED_HOSTS. Django will reject all requests in production mode. "
            "Your website won't be accessible externally without properly configuring this setting."
        )

    def success_host_created(self, host):
        self.console_manager.print_success(f"Host: {host} was successfully added")

    def success_hosts_removed(self, hosts):
        hosts_str = ", ".join(hosts)
        self.console_manager.print_success(
            f"Hosts: {hosts_str} were successfully deleted"
        )
