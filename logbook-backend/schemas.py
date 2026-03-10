from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
import datetime

# =======================
# AUTH SCHEMAS
# =======================
class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# =======================
# AI SCHEMAS
# =======================
class AIQueryRequest(BaseModel):
    question: str
    experiments: List[Any] = []

class AIQueryResponse(BaseModel):
    answer: str
    referenced_experiments: List[str] = []
