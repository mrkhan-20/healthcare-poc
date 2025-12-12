
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from services.auth_service import create_access_token, verify_token
from schemas import LoginRequest, LoginResponse

router = APIRouter(prefix='/auth', tags=['auth'])
security = HTTPBearer()


async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Dependency to get the current authenticated user."""
    token = creds.credentials
    return verify_token(token)


@router.post('/login', response_model=LoginResponse)
async def login(request: LoginRequest):
    """Mock login endpoint - accepts any username for PoC."""
    token = create_access_token(subject=request.username)
    return LoginResponse(access_token=token)

