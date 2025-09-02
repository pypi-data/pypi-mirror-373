from ..settings_service import DjangoSettingsService
from .allowed_hosts_handler_display import AllowedHostsHandlerDisplay


class AllowedHostsHandler:
    def __init__(
        self,
        settings_service: DjangoSettingsService,
        display: AllowedHostsHandlerDisplay,
    ):
        self.settings_service = settings_service
        self.display = display

    def handle_allowed_hosts(self):
        allowed_hosts = self.settings_service.find_in_settings("ALLOWED_HOSTS")
        if not allowed_hosts:
            self.display.warning_empty_hosts()
            return self._add_new_host()

        response, hosts = self.display.prompt_allowed_hosts_manager(allowed_hosts)
        if response == "create":
            return self._add_new_host()
        elif response == "delete":
            return self._remove_host(hosts)
        else:
            return 0

    def edit_allowed_hosts(self, host, operation="add"):
        """
        Modify the ALLOWED_HOSTS setting by adding or removing hosts

        Args:
            host (str or list): The host(s) to add or remove
            operation (str): The operation to perform ('add' or 'remove')

        Returns:
            tuple: (bool - success, list - current hosts)
        """
        # Get the current ALLOWED_HOSTS
        current_hosts = self.settings_service.find_in_settings(
            "ALLOWED_HOSTS", default=[]
        )

        # If it's a string (like "*"), convert to a list
        if isinstance(current_hosts, str):
            current_hosts = [current_hosts]
        elif current_hosts is None:
            current_hosts = []

        # Convert single host to list for consistent processing
        hosts_to_process = [host] if isinstance(host, str) else host

        if operation == "add":
            # Add hosts that aren't already in the list
            updated_hosts = current_hosts.copy()
            for h in hosts_to_process:
                if h not in current_hosts:
                    updated_hosts.append(h)
        elif operation == "remove":
            # Remove hosts that are in the list
            updated_hosts = [h for h in current_hosts if h not in hosts_to_process]
        else:
            return False, current_hosts  # Invalid operation

        # Update the setting
        success = self.settings_service.edit_settings("ALLOWED_HOSTS", updated_hosts)

        return success, updated_hosts

    def _add_new_host(self):
        try:
            host = self.display.prompt_allowed_hosts_input()
            self.edit_allowed_hosts(host)
        except:
            # TODO: if edit_allowed_hosts is cancelled there it returns None and crashes
            pass
        self.display.success_host_created(host)
        return self.handle_allowed_hosts()

    def _remove_host(self, hosts_to_remove):
        self.edit_allowed_hosts(hosts_to_remove, operation="remove")
        self.display.success_hosts_removed(hosts_to_remove)
        return self.handle_allowed_hosts()
