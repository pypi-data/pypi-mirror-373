#TODO: Automatic discovery of formatters
from .email.bazos_sk_email_formatter import BazosSkEmailFormatter

FORMATTERS: dict[str, type] = {
    'email_formatter': BazosSkEmailFormatter
}