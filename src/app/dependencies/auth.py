from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.app.database import get_db
from src.app.models.user import User
from src.app.services.token_service import TokenService
from src.app.utils.auth import verify_token

# OAuth2 인증 체계 설정 (토큰 URL 지정)
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
bearer_scheme = HTTPBearer()

"""
토큰에서 현재 사용자 정보를 가져오는 의존성 함수
"""
# token: str = Depends(oauth2_scheme)
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    # 토큰이 블랙리스트에 있는지 확인
    token = credentials.credentials
    
    if TokenService.is_token_blacklisted(token):
        raise HTTPException(
            status_code=401,
            detail="만료된 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 토큰 검증
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="인증되지 않은 사용자입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 토큰에서 사용자명 추출
    username = payload.get("username")
    if username is None:
        raise HTTPException(
            status_code=401,
            detail="인증되지 않은 사용자입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 사용자 조회
    query = (
        select(User).
        where(User.username == username)
    )
    user = db.execute(query).scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="사용자를 찾을 수 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user