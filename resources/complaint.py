from fastapi import APIRouter, Depends, status
from starlette.requests import Request

from managers.complaint import ComplaintManager
from managers.auth import oauth2_scheme, is_complainer, is_admin, is_approver
from schemas.request.complaint import ComplaintIn
from schemas.response.complaint import ComplaintOut

router = APIRouter(tags=["Complaints"])


@router.get(
    "/complaints/",
    dependencies=[Depends(oauth2_scheme)],
    response_model=list[ComplaintOut],
)
async def get_complaints(request: Request):
    user = request.state.user
    return await ComplaintManager.get_complaints(user)


@router.post(
    "/complaints/",
    dependencies=[Depends(oauth2_scheme), Depends(is_complainer)],
    response_model=ComplaintOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_complaint(request: Request, complaint: ComplaintIn):
    user = request.state.user
    return await ComplaintManager.create_complaint(complaint.model_dump(), user)


@router.delete(
    "/complaints/{complaint_id}/",
    dependencies=[Depends(oauth2_scheme), Depends(is_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_complaint(complaint_id: int):
    await ComplaintManager.delete_complaint(complaint_id)


@router.put(
    "/complaints/{complaint_id}/approve",
    dependencies=[Depends(oauth2_scheme), Depends(is_approver)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def approve_complaint(complaint_id: int):
    await ComplaintManager.approve(complaint_id)


@router.put(
    "/complaints/{complaint_id}/reject",
    dependencies=[Depends(oauth2_scheme), Depends(is_approver)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def reject_complaint(complaint_id: int):
    await ComplaintManager.reject(complaint_id)
