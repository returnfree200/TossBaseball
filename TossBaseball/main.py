from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# [추가] 입력 누락/형식 에러 시 과제 규격 {"error": "INVALID_INPUT"}으로 통일
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": "INVALID_INPUT"},
    )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1) POST /users
@app.post("/users", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # email 중복 체크
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail={"error": "EMAIL_ALREADY_EXISTS"})
    
    new_user = models.User(email=user.email, name=user.name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 2) POST /users/{user_id}/memos
@app.post("/users/{user_id}/memos", response_model=schemas.MemoOut)
def create_memo(user_id: int, memo: schemas.MemoCreate, db: Session = Depends(get_db)):
    # user_id 존재 여부 확인
    db_user = db.get(models.User, user_id)
    if not db_user:
        raise HTTPException(status_code=400, detail={"error": "USER_NOT_FOUND"})
    
    new_memo = models.Memo(user_id=user_id, title=memo.title, content=memo.content)
    db.add(new_memo)
    db.commit()
    db.refresh(new_memo)
    return new_memo

    

# 3) GET /memos (작성자 포함, JOIN 필수)
@app.get("/memos", response_model=List[schemas.MemoOut])
def read_all_memos(db: Session = Depends(get_db)):
    # [요구조건] joinedload를 사용하여 N+1 방지 및 한 번에 JOIN 조회
    memos = db.query(models.Memo).options(joinedload(models.Memo.author)).all()
    if memos is None: # 논리적 예외 상황 대응
        raise HTTPException(status_code=400, detail={"error": "BAD_REQUEST"})
    return memos

# 4) GET /users/{user_id}/memos
@app.get("/users/{user_id}/memos", response_model=List[schemas.MemoOut])
def read_user_memos(user_id: int, db: Session = Depends(get_db)):
    # user_id 존재 여부 확인
    db_user = db.get(models.User, user_id)
    if not db_user:
        raise HTTPException(status_code=400, detail={"error": "USER_NOT_FOUND"})
    
    return db.query(models.Memo).filter(models.Memo.user_id == user_id).all()