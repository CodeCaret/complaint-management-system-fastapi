from pwdlib import PasswordHash
from asyncpg import UniqueViolationError
from fastapi import HTTPException

from db import database
from models import user
from managers.auth import AuthManager
from models.user import RoleType

password_hash = PasswordHash.recommended()


class UserManager:

    @staticmethod
    async def register(user_data):
        user_data["password"] = password_hash.hash(password=user_data["password"])
        try:
            id_ = await database.execute(user.insert().values(**user_data))
        except UniqueViolationError:
            raise HTTPException(400, "User with this email already exists")
        user_do = await database.fetch_one(user.select().where(user.c.id == id_))
        return AuthManager.encode_token(user_do)

    @staticmethod
    async def login(user_data):
        user_do = await database.fetch_one(
            user.select().where(user.c.email == user_data["email"])
        )
        if not user_do:
            raise HTTPException(400, "Wrong email or password")
        elif not password_hash.verify(user_data["password"], user_do["password"]):
            raise HTTPException(400, "Wrong email or password")
        return AuthManager.encode_token(user_do), user_do["role"]

    @staticmethod
    async def get_all_users():
        return await database.fetch_all(user.select())

    @staticmethod
    async def get_user_by_email(email):
        return await database.fetch_all(user.select().where(user.c.email == email))

    @staticmethod
    async def change_role(role: RoleType, user_id):
        await database.execute(
            user.update().where(user.c.id == user_id).values(role=role)
        )
