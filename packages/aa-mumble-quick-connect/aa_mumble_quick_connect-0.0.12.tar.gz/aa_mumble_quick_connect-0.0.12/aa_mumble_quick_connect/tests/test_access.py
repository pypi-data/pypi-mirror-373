"""
Test auth_hooks
"""

# Standard Library
from http import HTTPStatus

# Django
from django.test import TestCase, modify_settings
from django.urls import reverse

# Alliance Auth (External Libs)
from app_utils.testing import create_fake_user

# AA Mumble Quick Connect
from aa_mumble_quick_connect.tests.utils import response_content_to_str


class TestAccess(TestCase):
    """
    Test access
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up groups and users
        """

        super().setUpClass()

        # User
        cls.user_1001 = create_fake_user(
            character_id=1001,
            character_name="Jean Luc Picard",
            permissions=[
                "aa_mumble_quick_connect.basic_access",
                "mumble.access_mumble",
            ],
        )

        cls.user_1002 = create_fake_user(
            character_id=1002,
            character_name="William Riker",
            permissions=["mumble.access_mumble"],
        )

        cls.user_1003 = create_fake_user(
            character_id=1003,
            character_name="Worf",
            permissions=["aa_mumble_quick_connect.basic_access"],
        )

        cls.user_1004 = create_fake_user(
            character_id=1004, character_name="Wesley Crusher"
        )

        cls.html_menu = f"""
            <li class="d-flex flex-wrap m-2 p-2 pt-0 pb-0 mt-0 mb-0 me-0 pe-0">
                <i class="nav-link fa-solid fa-headphones-simple fa-fw align-self-center me-3 active"></i>
                <a class="nav-link flex-fill align-self-center me-auto active" href="{reverse('aa_mumble_quick_connect:index')}">
                    Mumble Quick Connect
                </a>
            </li>
        """

        cls.header_top = '<div class="navbar-brand">Mumble Quick Connect</div>'

    @modify_settings(INSTALLED_APPS={"append": "allianceauth.services.modules.mumble"})
    def test_access_for_user_with_permission(self):
        """
        Test access for user with permission

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_1001)

        response = self.client.get(
            path=reverse(viewname="aa_mumble_quick_connect:index")
        )

        self.assertEqual(first=response.status_code, second=HTTPStatus.OK)
        self.assertInHTML(
            needle=self.html_menu, haystack=response_content_to_str(response)
        )
        self.assertInHTML(
            needle=self.header_top, haystack=response_content_to_str(response)
        )

    @modify_settings(INSTALLED_APPS={"append": "allianceauth.services.modules.mumble"})
    def test_access_for_user_with_just_mumble_permission(self):
        """
        Test access for user with just mumble permission

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_1002)

        response = self.client.get(
            path=reverse(viewname="aa_mumble_quick_connect:index")
        )

        self.assertEqual(first=response.status_code, second=HTTPStatus.FOUND)
        self.assertNotIn(
            member=self.html_menu, container=response_content_to_str(response)
        )
        self.assertNotIn(
            member=self.header_top, container=response_content_to_str(response)
        )

    @modify_settings(INSTALLED_APPS={"append": "allianceauth.services.modules.mumble"})
    def test_access_for_user_with_just_aa_mumble_quick_connect_permission(self):
        """
        Test access for user with just aa_mumble_quick_connect permission

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_1003)

        response = self.client.get(
            path=reverse(viewname="aa_mumble_quick_connect:index")
        )

        self.assertEqual(first=response.status_code, second=HTTPStatus.FOUND)
        self.assertNotIn(
            member=self.html_menu, container=response_content_to_str(response)
        )
        self.assertNotIn(
            member=self.header_top, container=response_content_to_str(response)
        )

    @modify_settings(INSTALLED_APPS={"append": "allianceauth.services.modules.mumble"})
    def test_access_for_user_without_permission(self):
        """
        Test access for user without permission

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_1004)

        response = self.client.get(
            path=reverse(viewname="aa_mumble_quick_connect:index")
        )

        self.assertEqual(first=response.status_code, second=HTTPStatus.FOUND)
        self.assertNotIn(
            member=self.html_menu, container=response_content_to_str(response)
        )
        self.assertNotIn(
            member=self.header_top, container=response_content_to_str(response)
        )
