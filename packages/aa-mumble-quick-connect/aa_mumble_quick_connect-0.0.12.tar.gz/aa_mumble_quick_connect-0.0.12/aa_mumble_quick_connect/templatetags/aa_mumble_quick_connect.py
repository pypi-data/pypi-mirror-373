"""
Template tags for the aa-mumble-quick-connect app.
"""

# Django
from django import template

register = template.Library()


@register.simple_tag
def aa_mumble_quick_connect_link(channel_url=None, username=None):
    """
    Create a mumble quick connect link

    :param channel_url: Mumble channel URL
    :type channel_url: str
    :param username: Username
    :type username: str
    :return: Mumble quick connect link
    :rtype: str
    """

    return channel_url.replace("mumble://", f"mumble://{username}@")
