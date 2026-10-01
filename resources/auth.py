from fastapi import APIRouter, status

from managers.user import UserManager
from schemas.request.user import UserRegisterIn, UserLoginIn

router = APIRouter(
    tags=["Auth"],
)


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegisterIn):
    token = await UserManager.register(
        user_data.model_dump()
    )
    return {"token": token}


@router.post("/login/")
async def login(user_data: UserLoginIn):
    token, role = await UserManager.login(user_data.model_dump())
    return {"token": token, "role": role}
