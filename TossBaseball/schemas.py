from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

# 1. 유저 관련 규격
class UserCreate(BaseModel):
    email: EmailStr  # Pydantic이 이메일 형식을 자동으로 검사합니다
    name: str

class UserOut(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy 객체를 Pydantic 모델로 변환 허용

# 2. 메모 관련 규격
class MemoCreate(BaseModel):
    title: str
    content: str

class MemoOut(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    created_at: datetime
    # JOIN 조회를 위해 작성자 정보를 포함 (Optional)
    user: Optional[UserOut] = None 

    class Config:
        from_attributes = True

# 3. 공통 에러 응답 규격 (요구사항 반영)
class ErrorResponse(BaseModel):
    error: str