"""
Admin models
"""

# Django
from django.contrib import admin

# AA Mumble Quick Connect
from aa_mumble_quick_connect.models import MumbleLink, Section


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    """
    SectionAdmin
    """

    list_display = ("name",)
    ordering = ("name",)


@admin.register(MumbleLink)
class MumbleLinkAdmin(admin.ModelAdmin):
    """
    MumbleLinkAdmin
    """

    list_display = ("name", "section", "url", "disable_url_verification")
    ordering = ("section", "name")
