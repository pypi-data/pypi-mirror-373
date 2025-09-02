"""Authentication router for GitHub OAuth integration."""

import httpx
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..database import get_db
from ..models.user import User

router = APIRouter()
security = HTTPBearer(auto_error=False)

settings = get_settings()


class GitHubAuthRequest(BaseModel):
    """Request model for GitHub auth."""
    code: str
    state: Optional[str] = None


class AuthResponse(BaseModel):
    """Response model for successful authentication."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class GitHubUser(BaseModel):
    """GitHub user profile model."""
    id: int
    login: str
    email: Optional[str]
    name: Optional[str]
    avatar_url: str
    html_url: str


async def get_github_user_info(access_token: str) -> GitHubUser:
    """Get user info from GitHub API."""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        # Get user profile
        response = await client.get("https://api.github.com/user", headers=headers)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to get GitHub user info"
            )
        
        user_data = response.json()
        
        # Get primary email if not public
        if not user_data.get("email"):
            email_response = await client.get("https://api.github.com/user/emails", headers=headers)
            if email_response.status_code == 200:
                emails = email_response.json()
                primary_email = next((email["email"] for email in emails if email["primary"]), None)
                user_data["email"] = primary_email
        
        return GitHubUser(**user_data)


def create_access_token(user_id: str) -> tuple[str, datetime]:
    """Create JWT access token."""
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt, expire


async def get_current_user_or_local(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token or local mode."""
    
    # Check for local mode header first
    local_mode = request.headers.get("X-Local-Mode")
    
    if local_mode == "true":
        # Return a fake local user for local mode
        user = User(
            email="local@mem8.com",
            username="local",
            full_name="Local User",
            hashed_password=None,
            is_active=True,
            is_superuser=False
        )
        user.id = "local-user-id"  # Set ID manually
        return user
    
    # Normal JWT authentication
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
        
    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Get user from database
    result = await db.execute(
        User.__table__.select().where(User.id == user_id)
    )
    user = result.first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

# Keep the original function for backward compatibility
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Get user from database
    result = await db.execute(
        User.__table__.select().where(User.id == user_id)
    )
    user = result.first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@router.post("/github/callback", response_model=AuthResponse)
async def github_callback(
    auth_request: GitHubAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """Handle GitHub OAuth callback."""
    
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": auth_request.code,
            },
            headers={"Accept": "application/json"}
        )
        
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for token"
            )
        
        token_data = token_response.json()
        print(f"DEBUG: GitHub token response: {token_data}")  # Debug logging
        github_access_token = token_data.get("access_token")
        
        if not github_access_token:
            error_description = token_data.get("error_description", "Unknown error")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No access token received: {error_description}"
            )
    
    # Get user info from GitHub
    github_user = await get_github_user_info(github_access_token)
    
    # Find or create user in database
    from sqlalchemy import select
    result = await db.execute(
        select(User).where(User.email == github_user.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Create new user using ORM
        new_user = User(
            email=github_user.email,
            username=github_user.login,
            full_name=github_user.name or github_user.login,
            hashed_password=None,  # OAuth users don't have passwords
            is_active=True,
            is_superuser=False,
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        user = new_user
    
    # Create access token
    access_token, expire = create_access_token(user.id)
    
    return AuthResponse(
        access_token=access_token,
        expires_in=int((expire - datetime.utcnow()).total_seconds()),
        user={
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "avatar_url": github_user.avatar_url,
        }
    )


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
    }


@router.post("/logout")
async def logout():
    """Logout endpoint (client should delete token)."""
    return {"message": "Successfully logged out"}


# GitHub OAuth URLs for frontend
@router.get("/github/url")
async def get_github_auth_url():
    """Get GitHub OAuth authorization URL."""
    auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.github_client_id}"
        f"&redirect_uri={settings.github_redirect_uri}"
        f"&scope=user:email"
        f"&state=random_state_string"
    )
    
    return {"auth_url": auth_url}
