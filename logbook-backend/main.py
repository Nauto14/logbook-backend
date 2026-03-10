import os
import models, schemas
from database import engine, SessionLocal
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import traceback

from auth import hash_password, verify_password, create_access_token, get_current_user
import ai as ai_module

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Physics Logbook V2")

# CORS — configurable via CORS_ORIGINS env var (comma-separated).
# Default to common frontend URLs in case it's not set.
_cors_origins_env = os.environ.get("CORS_ORIGINS", "http://localhost:3000,https://logbook-frontend.vercel.app,*")
if _cors_origins_env == "*":
    _cors_origins = ["*"]
else:
    _cors_origins = [origin.strip() for origin in _cors_origins_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# ─── AUTH ENDPOINTS ───────────────────────────────────────────────

@app.post("/api/auth/register", response_model=schemas.TokenResponse)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # Check for existing email
        if db.query(models.User).filter(models.User.email == user_data.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        # Check for existing username
        if db.query(models.User).filter(models.User.username == user_data.username).first():
            raise HTTPException(status_code=400, detail="Username already taken")
        # Create user
        db_user = models.User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hash_password(user_data.password),
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        # Generate token
        token = create_access_token({"sub": str(db_user.id)})
        return schemas.TokenResponse(
            access_token=token,
            user=schemas.UserResponse.model_validate(db_user),
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print("REGISTER ERROR:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login", response_model=schemas.TokenResponse)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": str(user.id)})
    return schemas.TokenResponse(
        access_token=token,
        user=schemas.UserResponse.model_validate(user),
    )

@app.get("/api/auth/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    return schemas.UserResponse.model_validate(current_user)

# ─── AI ENDPOINT ──────────────────────────────────────────────────

@app.post("/api/ai/query", response_model=schemas.AIQueryResponse)
def ai_query(
    request: schemas.AIQueryRequest,
    current_user: models.User = Depends(get_current_user),
):
    result = ai_module.query_experiments(request.question, request.experiments)
    return schemas.AIQueryResponse(**result)

# All experiment CRUD operations, sample retrieving, and file serving
# have been moved to the client-side using IndexedDB (Dexie).
# The endpoints: POST /api/experiments/, GET /api/experiments/,
# GET /api/experiments/{id}, GET /api/samples/, PUT /api/experiments/{id}
# are now explicitly removed to enforce local-first storage.
