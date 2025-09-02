# /app/auth.py
import os
from typing import Optional, AsyncGenerator
from uuid import UUID

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend
from fastapi_users.authentication.transport import BearerTransport
from fastapi_users.authentication.strategy import JWTStrategy

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from ..database import get_async_session, async_session_factory

from ..models import User , Base # FIX: Only import the User model (and other necessary Pydantic schemas if any were used directly here)


# --- User Manager ---
class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    RESET_PASSWORD_TOKEN_LIFETIME_SECONDS = 60 * 60 * 24 # 1 day
    VERIFICATION_TOKEN_LIFETIME_SECONDS = 60 * 60 * 24 # 1 day

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

# --- Authentication Backend ---
SECRET = os.getenv("AUTH_SECRET_KEY", "your-super-secret-key-that-should-be-randomly-generated-and-long")

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# Add this function at the end of the file
async def validate_token(token: str) -> Optional[User]:
    """Validate a JWT token and return the user if valid."""
    try:
        user_id = fastapi_users.authenticator._decode_jwt(
            token,
            fastapi_users.authenticator._get_strategy().secret,
            fastapi_users.authenticator._get_strategy().lifetime_seconds
        )
        async with async_session_factory() as session:
            user_db = SQLAlchemyUserDatabase(session, User)
            user = await user_db.get(user_id)
            return user
    except Exception:
        return None

# --- FastAPI-Users Dependency Functions ---
async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """Dependency to get a SQLAlchemyUserDatabase instance."""
    yield SQLAlchemyUserDatabase(session, User)

async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    """Dependency to get a UserManager instance."""
    yield UserManager(user_db)

# --- FastAPIUsers Instance ---
fastapi_users = FastAPIUsers[User, UUID](User, [auth_backend])

# --- Current User Dependencies ---
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
