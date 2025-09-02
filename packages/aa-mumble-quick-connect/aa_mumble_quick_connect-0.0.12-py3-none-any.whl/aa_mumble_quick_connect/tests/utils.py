"""
Helper for our tests
"""

# Django
from django.core.handlers.wsgi import WSGIRequest
from django.template import Context, Template


def render_template(string, context=None):
    """
    Helper to render templates
    :param string:
    :param context:
    :return:
    """

    context = context or {}
    context = Context(dict_=context)

    return Template(template_string=string).render(context=context)


def response_content_to_str(response: WSGIRequest) -> str:
    """
    Return the content of a WSGIRequest response as string

    :param response:
    :type response:
    :return:
    :rtype:
    """

    return response.content.decode(response.charset)
