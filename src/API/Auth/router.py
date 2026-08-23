from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.API.Auth.models import User
from src.API.Auth.schemas import (
    SignUpRequest,
    UserResponse,
    SignInRequest,
    TokenResponse,
)
from src.API.database import get_db
from src.API.Auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from src.API.Auth.dependencies import get_current_user


router = APIRouter(
    prefix="/Auth",
    tags=["Authentication"],
)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(request: SignUpRequest, db: Session = Depends(get_db)):
    existing_user = db.scalar(
        select(User).where(
            (User.email == request.email)
            | (User.username == request.username)
        )
    )

    if existing_user:
        if existing_user.email == request.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered.",
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is already taken.",
        )

    user = User(
        username=request.username,
        email=request.email,
        password_hash=hash_password(request.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/signin", response_model=TokenResponse)
def signin(request: SignInRequest, db: Session = Depends(get_db)):
    user = db.scalar(
        select(User).where(User.email == request.email)
    )

    if not user or not verify_password(
        request.password, user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(
        user.id,
        user.token_version,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.token_version += 1
    db.add(current_user)
    db.commit()

    return {"message": "Logged out successfully."}
