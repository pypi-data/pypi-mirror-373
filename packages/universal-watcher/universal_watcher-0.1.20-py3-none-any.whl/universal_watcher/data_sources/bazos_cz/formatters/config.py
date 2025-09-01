#TODO: Automatic discovery of formatters
from .email.bazos_cz_email_formatter import BazosCzEmailFormatter

FORMATTERS: dict[str, type] = {
    'email_formatter': BazosCzEmailFormatter
}