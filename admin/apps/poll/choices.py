# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _

CHOICES_STATUS = (
    ("ON", _("On")),
    ("OFF", _("Off")),
    ("S", _("Suspend")),
)

CHOICES_DELEGATE = (
    ("OK", _("Accepted")),
    ("KO", _("Denied")),
)

CHOICES_I18N = (
    ("es", _("Spanish")),
    ("ca", _("Catalan")),
)
