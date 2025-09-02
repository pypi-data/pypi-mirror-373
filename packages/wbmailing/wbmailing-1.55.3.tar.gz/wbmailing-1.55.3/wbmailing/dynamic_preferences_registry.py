from re import fullmatch

from django.forms import ValidationError
from django.utils.translation import gettext as _
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import BooleanPreference, StringPreference

mailing_section = Section("wbmailing")


@global_preferences_registry.register
class DefaultSourceMailPreference(StringPreference):
    section = mailing_section
    name = "default_source_mail"
    default = "info@stainly-bench.com"

    verbose_name = _("Default Source Mail Preference")
    help_text = _("The default address used to send emails from")

    def validate(self, value):
        if not fullmatch(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValidationError(_("Not a valid email format"))


@global_preferences_registry.register
class AutomaticallyApproveUnsubscriptionRequestFromHardBound(BooleanPreference):
    section = mailing_section
    name = "automatically_approve_unsubscription_request_from_hard_bounce"
    default = False

    verbose_name = _("Automatically approve unsubscription request from hard bounce")
    help_text = _(
        "Automatically approve unsubscription request from hard bounce received from the ESP tracking system"
    )
