from pydantic import BaseModel, SecretStr
from enum import Enum


class EncryptionEnum(str, Enum):
    SSL = "SSL"
    TLS = "TLS"
    STARTTLS = "STARTTLS"


class EmailSmtpConfig(BaseModel):
    host: str
    port: int
    encryption: EncryptionEnum
    username: str
    password: SecretStr
    sender_email: str
