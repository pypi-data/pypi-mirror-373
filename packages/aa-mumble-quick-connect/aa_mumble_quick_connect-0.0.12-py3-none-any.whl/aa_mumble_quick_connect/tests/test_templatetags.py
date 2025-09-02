"""
Test the apps' template tags
"""

# Django
from django.template import Context, Template
from django.test import TestCase, override_settings


class TestQuickConnectLinkTemplateTag(TestCase):
    """
    Test aa_mumble_quick_connect template tag
    """

    @override_settings(DEBUG=False)
    def test_aa_mumble_quick_connect(self) -> None:
        """
        Test aa_mumble_quick_connect template tag

        :return:
        :rtype:
        """

        context = Context({"mumble_link": "mumble://example.com", "username": "foobar"})
        template_to_render = Template(
            template_string=(
                "{% load aa_mumble_quick_connect %}"
                "{% aa_mumble_quick_connect_link mumble_link username %}"
            )
        )

        rendered_template = template_to_render.render(context=context)
        expected = "mumble://foobar@example.com"

        self.assertEqual(first=rendered_template, second=expected)
