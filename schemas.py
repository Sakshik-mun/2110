from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProfileIn(BaseModel):
    monthly_income: float = Field(ge=0)
    monthly_expenses: float = Field(ge=0)
    monthly_emi: float = Field(ge=0)
    total_debt: float = Field(ge=0)
    credit_limit: float = Field(ge=0)
    credit_used: float = Field(ge=0)
    active_loans: int = Field(ge=0, le=100)
    missed_payments: int = Field(ge=0, le=1000)
    savings: float = Field(ge=0)
    cibil_score: int = Field(ge=300, le=900)
    goal: str = Field(default="", max_length=255)


class ScoreIn(BaseModel):
    score: int = Field(ge=300, le=900)


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
