"""
Dependency checks for the `aa-mumble-quick-connect` app
"""

# Django
from django.apps import apps


def mumble_service_installed() -> bool:
    """
    Check if `allianceauth.services.modules.mumble` is installed and active

    :return: True if installed, False otherwise
    :rtype: bool
    """

    return apps.is_installed(app_name="allianceauth.services.modules.mumble")
