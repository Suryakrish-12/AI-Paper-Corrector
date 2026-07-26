from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models import User, Student, Faculty, Department, Course
from app.schemas import Token, UserCreate, UserResponse
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
import random

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new system user and automatically builds profile structures (Student/Faculty) with random registrations if needed.
    """
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_pwd = get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        hashed_password=hashed_pwd,
        name=user_in.name,
        role=user_in.role,
        is_verified=True  # Auto-verify true for demo environment
    )
    db.add(user)
    db.flush()
    
    # Build related profiles automatically to support immediate logins
    if user.role == "STUDENT":
        dept = db.query(Department).first()
        course = db.query(Course).first()
        reg_num = f"2026{random.randint(100000, 999999)}"
        
        student = Student(
            user_id=user.id,
            register_number=reg_num,
            department_id=dept.id if dept else 1,
            course_id=course.id if course else 1,
            semester=1
        )
        db.add(student)
        
    elif user.role in ["FACULTY", "HOD", "ADMIN"]:
        dept = db.query(Department).first()
        faculty = Faculty(
            user_id=user.id,
            department_id=dept.id if dept else 1,
            designation="Professor" if user.role == "HOD" else "Assistant Professor"
        )
        db.add(faculty)
        
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Standard OAuth2 compatible token login flow. Returns bearer JWT.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Retrieves currently active user metadata.
    """
    return current_user

@router.post("/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    """
    Mock API for email password resetting.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")
    return {"message": f"Verification reset code sent to {email}"}
