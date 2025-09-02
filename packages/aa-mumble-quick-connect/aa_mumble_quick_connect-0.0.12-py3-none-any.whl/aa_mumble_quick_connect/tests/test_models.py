# Django
from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

# AA Mumble Quick Connect
from aa_mumble_quick_connect.models import MumbleLink, Section, validate_mumble_url


class TestSection(TestCase):
    """
    Tests for the `Section` model
    """

    def test_model_string_names(self):
        """
        Test model string name

        :return:
        :rtype:
        """

        section = Section(name="Foobar")
        section.save()
        expected_name = section.name
        self.assertEqual(first=str(section), second=expected_name)


class TestMumbleLink(TestCase):
    """
    Tests for the `MumbleLink` model
    """

    def test_model_string_names(self):
        """
        Test model string name

        :return:
        :rtype:
        """

        section = MumbleLink(name="Foobar")
        section.save()
        expected_name = section.name
        self.assertEqual(first=str(section), second=expected_name)

    @override_settings(MUMBLE_URL="mumble.example.com")
    def test_validate_mumble_url_with_valid_url(self):
        """
        Test validate Mumble URL with valid URL

        :return:
        :rtype:
        """

        expected_mumble_base_url = f"mumble://{settings.MUMBLE_URL}"

        self.assertEqual(
            first=validate_mumble_url(url=f"mumble://{settings.MUMBLE_URL}"),
            second=expected_mumble_base_url,
        )

    @override_settings(MUMBLE_URL="mumble.example.com")
    def test_validate_mumble_url_with_invalid_url(self):
        """
        Test validate Mumble URL with invalid URL raises ValidationError

        :return:
        :rtype:
        """

        expected_mumble_base_url = f"mumble://{settings.MUMBLE_URL}"

        with self.assertRaisesMessage(
            expected_exception=ValidationError,
            expected_message=f'The Mumble channel URL must start with "{expected_mumble_base_url}"',
        ):
            validate_mumble_url("mumble://example.com")

    @override_settings(MUMBLE_URL="mumble.example.com")
    def test_validate_mumble_url_with_disabled_url_verification(self):
        """
        Test validate Mumble URL with disabled URL verification

        :return:
        :rtype:
        """

        self.assertEqual(
            first=validate_mumble_url(
                url="mumble://example.com", disable_url_verification=True
            ),
            second="mumble://example.com",
        )

    @override_settings(MUMBLE_URL="mumble.example.com")
    def test_validate_mumble_url_with_invalid_url_protocol(self):
        """
        Test validate Mumble URL with invalid URL protocol raises ValidationError

        :return:
        :rtype:
        """

        with self.assertRaisesMessage(
            expected_exception=ValidationError,
            expected_message='The Mumble channel URL must start with "mumble://"',
        ):
            validate_mumble_url(url="https://example.com")

    @override_settings(MUMBLE_URL="mumble.example.com")
    def test_validate_mumble_url_with_invalid_url_protocol_and_disabled_url_verification(
        self,
    ):
        """
        Test validate Mumble URL with invalid URL protocol and disabled URL verification raises ValidationError

        :return:
        :rtype:
        """

        with self.assertRaisesMessage(
            expected_exception=ValidationError,
            expected_message='The Mumble channel URL must start with "mumble://"',
        ):
            validate_mumble_url(
                url="https://example.com", disable_url_verification=True
            )

    @override_settings(MUMBLE_URL="mumble.example.com")
    def test_save_with_valid_url(self):
        """
        Test save with valid URL

        :return:
        :rtype:
        """

        mumble_link = MumbleLink(
            name="Foobar",
            url="mumble://mumble.example.com",
            section=Section.objects.create(name="Foobar"),
        )
        mumble_link.save()

        self.assertEqual(first=mumble_link.url, second="mumble://mumble.example.com")

    @override_settings(MUMBLE_URL="mumble.example.com")
    def test_save_with_invalid_url_raises_validation_error(self):
        """
        Test save with invalid URL raises ValidationError

        :return:
        :rtype:
        """

        mumble_link = MumbleLink(
            name="Foobar",
            url="mumble://example.com",
            section=Section.objects.create(name="Foobar"),
        )

        expected_mumble_base_url = f"mumble://{settings.MUMBLE_URL}"

        with self.assertRaisesMessage(
            expected_exception=ValidationError,
            expected_message=f'The Mumble channel URL must start with "{expected_mumble_base_url}"',
        ):
            mumble_link.clean()

    @override_settings(MUMBLE_URL="mumble.example.com")
    def tes_save_with_invalid_url_does_not_raise_validation_error(self):
        """
        Test save with invalid URL does not raise ValidationError

        :return:
        :rtype:
        """

        mumble_link = MumbleLink(
            name="Foobar",
            url="mumble://example.com",
            section=Section.objects.create(name="Foobar"),
            disable_url_verification=True,
        )

        mumble_link.clean()
        mumble_link.save()

        self.assertEqual(first=mumble_link.url, second="mumble://example.com")
