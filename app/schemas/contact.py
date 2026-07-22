import re
from pydantic import BaseModel, Field, EmailStr, field_validator


PHONE_REGEX = re.compile(r"^\+?[\d\s\-\(\)]{10,20}$")


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    email: EmailStr
    comment: str = Field(..., min_length=10, max_length=2000)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Name is too short")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        value = value.strip()
        if not PHONE_REGEX.match(value):
            raise ValueError("Invalid phone format")
        digits = re.sub(r"\D", "", value)
        if len(digits) < 10:
            raise ValueError("Phone must contain at least 10 digits")
        return value

    @field_validator("comment")
    @classmethod
    def normalize_comment(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 10:
            raise ValueError("Comment is too short")
        return value


class ContactResponse(BaseModel):
    success: bool
    message: str
    correlation_id: str | None = None
    ai_analysis: dict | None = None
