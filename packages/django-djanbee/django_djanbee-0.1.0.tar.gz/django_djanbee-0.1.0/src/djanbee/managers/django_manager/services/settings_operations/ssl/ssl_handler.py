from ...settings_service import DjangoSettingsService
from .ssl_handler_display import SslHandlerDisplay
class SslHandler:
    
    def __init__(self, settings_service: DjangoSettingsService, display: SslHandlerDisplay):
        self.settings_service = settings_service
        self.display = display

    def handle_ssl(self):
        current_settings = self.get_ssl_settings_status()
        updated_settings = self.display.prompt_configure_menu(current_settings)
        if updated_settings is None:
            self.display.cancelled_operation()
            return

        results = self.update_ssl_settings(updated_settings, current_settings)


    def get_ssl_settings_status(self):
        """
        Check if SSL settings are enabled in the Django settings.py file
        
        Returns:
            list: List of names of SSL settings that are enabled
        """
        # Define the SSL-related settings to check
        ssl_settings = [
            'SECURE_SSL_REDIRECT',
            'SESSION_COOKIE_SECURE',
            'CSRF_COOKIE_SECURE',
            'SECURE_HSTS_SECONDS',
            'SECURE_HSTS_INCLUDE_SUBDOMAINS',
            'SECURE_HSTS_PRELOAD',
            'SECURE_PROXY_SSL_HEADER'
        ]
        
        enabled_settings = []
        
        # Check each setting
        for setting in ssl_settings:
            value = self.settings_service.find_in_settings(setting)
            # For boolean settings, only consider enabled if True
            if isinstance(value, bool) and value:
                enabled_settings.append(setting)
            # For HSTS seconds, consider enabled if > 0
            elif setting == 'SECURE_HSTS_SECONDS' and value is not None and value > 0:
                enabled_settings.append(setting)
            # For proxy header, consider enabled if it exists and is not None
            elif setting == 'SECURE_PROXY_SSL_HEADER' and value is not None:
                enabled_settings.append(setting)
        
        return enabled_settings
    
    

    def update_ssl_settings(self, updated_settings, current_settings):
        """
        Update SSL settings based on selected options.
        Only updates settings that have changed.

        Args:
            updated_settings (list): List of SSL setting names that should be enabled
            current_settings (list): List of SSL setting names currently enabled
        
        Returns:
            dict: Dictionary with information about which settings were updated
        """
        results = {}
        
        # Handle boolean settings that are simple True/False toggles
        boolean_settings = [
            'SECURE_SSL_REDIRECT',
            'SESSION_COOKIE_SECURE',
            'CSRF_COOKIE_SECURE',
            'SECURE_HSTS_INCLUDE_SUBDOMAINS',
            'SECURE_HSTS_PRELOAD'
        ]
        
        for setting in boolean_settings:
            # Check if there's a change needed
            should_be_enabled = setting in updated_settings
            is_currently_enabled = setting in current_settings
            
            # Only update if there's a change to make
            if should_be_enabled != is_currently_enabled:
                success = self.settings_service.edit_settings(setting, should_be_enabled)
                results[setting] = {
                    'success': success if isinstance(success, bool) else success[0],  # Handle tuple returns
                    'changed': True,
                    'new_value': should_be_enabled
                }
                
                # Display update notification
                self.display.success_update_bool_setting(setting, should_be_enabled)
            else:
                # No change needed
                results[setting] = {
                    'success': True,
                    'changed': False,
                    'new_value': should_be_enabled
                }
        
        # Handle HSTS seconds setting
        hsts_result = self.handle_hsts_seconds(updated_settings, current_settings)
        results['SECURE_HSTS_SECONDS'] = hsts_result
        
        proxy_result = self.handle_proxy_ssl_header(updated_settings, current_settings)
        results['SECURE_PROXY_SSL_HEADER'] = proxy_result

        # Add summary information
        changes_count = sum(1 for r in results.values() if r['changed'])
        if changes_count > 0:
            self.display.success_ssl_config()
        else:
            self.display.info_ssl_config()
        
        return results    

    def handle_hsts_seconds(self, updated_settings, current_settings):
        """
        Handle the SECURE_HSTS_SECONDS setting based on user selection.
        - If enabled, set to 10 seconds
        - If disabled, remove from settings file
        
        Args:
            updated_settings (list): List of settings names that should be enabled
            current_settings (list): List of settings names currently enabled
            
        Returns:
            dict: Information about the HSTS seconds update
        """
        hsts_in_updated = 'SECURE_HSTS_SECONDS' in updated_settings
        hsts_in_current = 'SECURE_HSTS_SECONDS' in current_settings
        
        # Get current value if it exists
        current_value = self.settings_service.find_in_settings('SECURE_HSTS_SECONDS', None)
        
        result = {
            'changed': False,
            'success': True,
            'action': 'none',
            'value': current_value
        }
        # If HSTS setting state has changed
        if hsts_in_updated != hsts_in_current or hsts_in_updated:
            if hsts_in_updated:
                # Prompt for new value if enabled
                new_value = self.display.input_hsts_seconds(current_value)
                if new_value is None:
                    return result  # User cancelled, return unchanged result
                
                # Only update if value actually changed
                if new_value != current_value:
                    success = self.settings_service.edit_settings('SECURE_HSTS_SECONDS', new_value)
                    result = {
                        'changed': True,
                        'success': success if isinstance(success, bool) else success[0],
                        'action': 'updated',
                        'value': new_value
                    }
                    self.display.success_update_hsts_seconds(new_value)
            else:
                # Setting should be disabled - remove it from settings
                success, message = self.settings_service.delete_setting('SECURE_HSTS_SECONDS')
                result = {
                    'changed': True,
                    'success': success,
                    'action': 'disabled',
                    'value': None,
                    'message': message
                }
                self.display.success_disable_hsts_seconds()
        
        return result

    def handle_proxy_ssl_header(self, updated_settings, current_settings):
        """
        Handle the SECURE_PROXY_SSL_HEADER setting based on user selection.
        Always sets to ('HTTP_X_FORWARDED_PROTO', 'https') if enabled.
        
        Args:
            updated_settings (list): List of settings names that should be enabled
            current_settings (list): List of settings names currently enabled
            
        Returns:
            dict: Information about the proxy SSL header update
        """
        proxy_in_updated = 'SECURE_PROXY_SSL_HEADER' in updated_settings
        proxy_in_current = 'SECURE_PROXY_SSL_HEADER' in current_settings
        
        # Get current value if it exists
        current_value = self.settings_service.find_in_settings('SECURE_PROXY_SSL_HEADER', None)
        
        # Standard value for this setting
        standard_value = ('HTTP_X_FORWARDED_PROTO', 'https')
        
        result = {
            'changed': False,
            'success': True,
            'action': 'none',
            'value': current_value
        }
        
        # If proxy setting state has changed
        if proxy_in_updated != proxy_in_current:
            if proxy_in_updated:
                # Get user's proxy header selection
                selected_header = self.display.prompt_select_proxy_header()
                if selected_header is None:
                    return result  # User cancelled, return unchanged result
                    
                # Setting should be enabled with selected value
                success = self.settings_service.edit_settings('SECURE_PROXY_SSL_HEADER', selected_header)
                result = {
                    'changed': True,
                    'success': success if isinstance(success, bool) else success[0],
                    'action': 'enabled',
                    'value': selected_header
                }
                # Display success message with the selected header name
                header_name = selected_header[0]  # First element of the tuple
                self.display.success_update_proxy_header(header_name)
            else:
                # Setting should be disabled - remove it from settings
                success, message = self.settings_service.delete_setting('SECURE_PROXY_SSL_HEADER')
                result = {
                    'changed': True,
                    'success': success,
                    'action': 'disabled',
                    'value': None,
                    'message': message
                }
                self.display.success_disable_proxy_header()
        # If setting is already enabled but user wants to change the value
        elif proxy_in_updated and proxy_in_current:
            # Get user's proxy header selection
            selected_header = self.display.prompt_select_proxy_header()
            if selected_header is None:
                return result  # User cancelled, return unchanged result
                
            # Only update if the selected value is different from current value
            if selected_header != current_value:
                success = self.settings_service.edit_settings('SECURE_PROXY_SSL_HEADER', selected_header)
                result = {
                    'changed': True,
                    'success': success if isinstance(success, bool) else success[0],
                    'action': 'updated',
                    'value': selected_header
                }
                header_name = selected_header[0]  # First element of the tuple
                self.display.success_update_proxy_header(header_name)

        return result
