"""
A simple singleton class that loads custom integration mappings, if available
"""

# pylint: disable=C0415


class IntegrationOverride:
    """
    Custom Mapping class for findings
    """

    from threading import Lock
    from typing import Any, Optional

    _instance = None
    _lock = Lock()  # Ensures thread safety for singleton instance creation

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:  # Double-checked locking
                    cls._instance = super(IntegrationOverride, cls).__new__(cls)
        return cls._instance

    def __init__(self, app):
        from rich.console import Console

        config = app.config
        self.app = app
        self.mapping = self._get_mapping(config)
        if not hasattr(self, "_initialized"):
            self.console = Console()
            self._log_mappings()
            self._initialized = True

    def _log_mappings(self):
        """
        Notify the user that overrides are found
        """
        from rich.table import Table

        table = Table(title="Custom Integration Mappings", show_header=True, header_style="bold magenta")
        table.add_column("Integration", width=12, style="cyan")
        table.add_column("Field", width=12, style="orange3")  # Ensure this color is supported
        table.add_column("Mapped Value", width=20, style="red")

        for integration, fields in self.mapping.items():
            for field, value in fields.items():
                if value != "default":
                    table.add_row(integration, field, value)

        if table.row_count > 0:
            self.console.print(table)

    def _get_mapping(self, config: dict) -> dict:
        """
        Loads the mapping configuration from the application config.

        :param dict config: The application configuration
        :return: The mapping configuration
        :rtype: dict
        """
        return config.get("findingFromMapping", {})

    def load(self, integration: Optional[str], field_name: Optional[str]) -> Optional[str]:
        """
        Retrieves the mapped field name for a given integration and field name.

        :param Optional[str] integration: The integration name
        :param Optional[str] field_name: The field name
        :return: The mapped field name
        :rtype: Optional[str]
        """
        if integration and field_name and self.mapping_exists(integration, field_name):
            integration_map = self.mapping.get(integration.lower(), {})
            # Find the actual key that matches case-insensitively
            for key in integration_map.keys():
                if key.lower() == field_name.lower():
                    return integration_map.get(key)
        return None

    def mapping_exists(self, integration: str, field_name: str) -> bool:
        """
        Checks if a mapping exists for a given integration and field name.

        :param str integration: The integration name
        :param str field_name: The field name
        :return: Whether the mapping exists
        :rtype: bool
        """
        if not integration or not field_name:
            return False
        the_map = self.mapping.get(integration.lower())
        if not the_map:
            return False
        # Find the actual key that matches case-insensitively
        for key in the_map.keys():
            if key.lower() == field_name.lower():
                return the_map.get(key) != "default"
        return False

    def field_map_validation(self, obj: Any, model_type: str) -> Optional[str]:
        """
        Validate a field mapping between a RegScale object/dictionary and dataset.

        :param Any obj: The object to validate
        :param str model_type: The model type, ie. asset, issue, etc.
        :return: The validated field
        :rtype: Optional[str]
        """
        match = None
        try:
            unique_override = self.app.config.get("uniqueOverride", {}).get(model_type, [])
            if not unique_override:
                return match

            regscale_field = unique_override[0]
            if not regscale_field:
                return match

            regscale_to_obj_mapping = {
                # Tenable SC -> RegScale object -> RegScale field
                "tenableasset": {
                    "asset": {
                        "ipAddress": "ip",
                        "name": "dnsName",
                        "dns": "dnsName",
                        "fqdn": "dnsName",
                    }
                },
                # dict key -> RegScale object -> RegScale field.  This could grow to be quite large.
                "dict": {
                    "asset": {
                        "ipAddress": "ipv4",
                        "name": "fqdn",
                        "dns": "fqdn",
                        "fqdn": "fqdn",
                    }
                },
            }
            # The type an associated fields we are able to override. Limited for now.
            supported_fields = {"asset": {"ipAddress", "name", "fqdn", "dns"}, "issue": {"dateFirstDetected"}}
            if regscale_field not in supported_fields.get(model_type.lower(), set()):
                return match

            model = obj.__class__.__name__.lower()
            mapped_field = regscale_to_obj_mapping.get(model, {}).get(model_type, {}).get(regscale_field)
            if not mapped_field:
                return match

            if isinstance(obj, dict):
                match = obj.get(mapped_field)
            elif hasattr(obj, mapped_field):
                match = getattr(obj, mapped_field)
        except (KeyError, AttributeError, IndexError, TypeError) as e:
            self.app.logger.warning("Error parsing uniqueOverride: %s", str(e))
        return match
