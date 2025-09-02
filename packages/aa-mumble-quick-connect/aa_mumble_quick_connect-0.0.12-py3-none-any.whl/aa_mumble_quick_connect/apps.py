"""
App Configuration
"""

# Django
from django.apps import AppConfig

# AA Mumble Quick Connect
from aa_mumble_quick_connect import __version__


class AaMumbleQuickConnectConfig(AppConfig):
    """
    App configuration
    """

    name = "aa_mumble_quick_connect"
    label = "aa_mumble_quick_connect"
    verbose_name = f"Mumble Quick Connect v{__version__}"
