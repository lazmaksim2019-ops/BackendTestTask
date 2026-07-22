from pydantic import BaseModel, Field, EmailStr


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=5, max_length=20)
    email: EmailStr
    comment: str = Field(..., min_length=1, max_length=2000)


class ContactResponse(BaseModel):
    success: bool
    message: str
    correlation_id: str | None = None
    ai_analysis: dict | None = None
