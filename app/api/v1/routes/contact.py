from fastapi import APIRouter, Depends, Request
from app.schemas.contact import ContactRequest, ContactResponse
from app.services.contact_service import ContactService
from app.core.dependencies import get_contact_service

router = APIRouter(tags=["contact"])


@router.post("/contact", response_model=ContactResponse, status_code=201)
async def submit_contact(
    data: ContactRequest,
    request: Request,
    service: ContactService = Depends(get_contact_service),
):
    correlation_id = getattr(request.state, "correlation_id", None)
    result = await service.process(data, correlation_id)
    return result
