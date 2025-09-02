"""
App Models
"""

# Django
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


def validate_mumble_url(url: str, disable_url_verification: bool = False) -> str:
    """
    Validate Mumble channel URL against the configured Mumble server

    :param url: URL to validate
    :type url: str
    :param disable_url_verification: Disable URL verification
    :type disable_url_verification: bool
    :return: Validated URL
    :rtype: str
    """

    if not url.startswith("mumble://"):
        raise ValidationError(
            {"url": _('The Mumble channel URL must start with "mumble://"')}
        )

    if not disable_url_verification:
        mumble_base_url = f"mumble://{settings.MUMBLE_URL}"

        if not url.startswith(mumble_base_url):
            raise ValidationError(
                {
                    "url": _(
                        _(f'The Mumble channel URL must start with "{mumble_base_url}"')
                    )
                }
            )

    return url


class General(models.Model):
    """
    Meta model for app permissions
    """

    class Meta:
        """
        Meta definitions
        """

        managed = False
        default_permissions = ()
        permissions = (("basic_access", _("Can access this app")),)


class Section(models.Model):
    """
    Section model
    """

    name = models.CharField(
        max_length=255, unique=True, help_text=_("Name of the section")
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("Section")
        verbose_name_plural = _("Sections")

    def __str__(self) -> str:
        """
        String representation

        :return: Name of the section
        :rtype: str
        """

        return self.name


class MumbleLink(models.Model):
    """
    Mumble link model
    """

    section = models.ForeignKey(
        to=Section,
        on_delete=models.SET_NULL,
        related_name="mumble_links",
        verbose_name=_("Section"),
        null=True,
        blank=True,
        help_text=_("Section the Mumble channel belongs to. (Optional)"),
    )
    name = models.CharField(max_length=255, help_text=_("Name of the Mumble channel"))
    url = models.CharField(
        max_length=255,
        help_text=_("URL to the channel"),
    )
    disable_url_verification = models.BooleanField(
        default=False,
        verbose_name=_("Disable Mumble channel URL verification"),
        help_text=_(
            "If checked, the Mumble channel URL will not be verified against what is "
            "configured for this Auth instance when saving the link. Only use this "
            "if you are sure the URL is correct and the Mumble server is controlled "
            "by this Auth instance."
        ),
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("Mumble Link")
        verbose_name_plural = _("Mumble Links")

    def __str__(self) -> str:
        """
        String representation

        :return: Name of the Mumble channel
        :rtype: str
        """

        return self.name

    def clean(self):
        """
        Clean method

        :param args: Arguments
        :type args: tuple
        :param kwargs: Keyword arguments
        :type kwargs: dict
        :return: None
        :rtype: None
        """

        # Validate Mumble URL
        self.url = validate_mumble_url(
            url=self.url, disable_url_verification=self.disable_url_verification
        )

        super().clean()  # pragma: no cover
