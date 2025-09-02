"""
App Views
"""

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render

# AA Mumble Quick Connect
from aa_mumble_quick_connect.dependency_checks import mumble_service_installed
from aa_mumble_quick_connect.models import MumbleLink, Section


@login_required
@permission_required("aa_mumble_quick_connect.basic_access")
@permission_required("mumble.access_mumble")
def index(request: WSGIRequest, section: str = None) -> HttpResponse:
    """
    Index view

    :param request: The request
    :type request: WSGIRequest
    :param section: The section (optional)
    :type section: str
    :return: The response
    :rtype: HttpResponse
    """

    channels_in_sections = Section.objects.prefetch_related("mumble_links").all()
    channels_without_sections = MumbleLink.objects.filter(section__isnull=True)

    context = {
        "mumble_service_installed": mumble_service_installed(),
        "channels_in_sections": channels_in_sections,
        "channels_without_sections": channels_without_sections,
        "section_highlight": section,
    }

    return render(
        request=request,
        template_name="aa_mumble_quick_connect/index.html",
        context=context,
    )
