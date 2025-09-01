import gettext as _gettext
import locale
from pathlib import Path

ASSIGNED_LOCALE = None


def set_language(language):
    ASSIGNED_LOCALE = language  # noqa: F841


def get_locale():
    if ASSIGNED_LOCALE is not None:
        return ASSIGNED_LOCALE

    system_locale, encoding = locale.getlocale()

    if system_locale is None:
        system_locale = 'en'

    return system_locale


language = get_locale().split('_')[0]

PACKAGE_DIR = Path(__file__).parent
LOCALE_DIR = PACKAGE_DIR.parent / 'locale'

translation = _gettext.translation('messages', localedir=LOCALE_DIR, languages=[language], fallback=True)
translation.install()

gettext = translation.gettext
ngettext = translation.ngettext
pgettext = translation.pgettext
npgettext = translation.npgettext
