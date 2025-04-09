from fastapi import APIRouter, Depends, HTTPException
from src.app.schemas.user import UserCreate, UserResponse
from src.app.services.user_service import UserService, get_user_service

router = APIRouter()

# 회원가입
@router.post(
        "/register", 
        response_model=UserResponse,
        summary="회원가입",
        description="새로운 사용자를 등록합니다.",
        responses={
            409: {
                "description": "중복된 이메일로 회원가입 시도",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "이미 존재하는 이메일입니다.",
                        }
                    }
                }
            }
        }
)
def register_user(user: UserCreate, user_service: UserService = Depends(get_user_service)):
    existed_user_email = user_service.get_user_by_email(user.email)

    if existed_user_email:
        raise HTTPException(
            status_code=409,
            detail="이미 존재하는 이메일입니다."
        )
    
    existed_user_name = user_service.get_user_by_username(user.username)

    if existed_user_name:
            raise HTTPException(
                status_code=409,
                detail="이미 존재하는 사용자 이름입니다."
            )
    
    created_user = user_service.create_user(user)

    return created_user