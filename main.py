import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import User, FinancialProfile, ScoreHistory, Recommendation
from schemas import RegisterIn, LoginIn, TokenOut, ProfileIn, ScoreIn, ChatIn
from auth import hash_password, verify_password, create_token, current_user
import analytics
import ai_service

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Credit Assistant API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_methods=["*"], allow_headers=["*"],
)

PROFILE_KEYS = ["monthly_income", "monthly_expenses", "monthly_emi", "total_debt", "credit_limit",
                "credit_used", "active_loans", "missed_payments", "savings", "cibil_score", "goal"]


def profile_dict(p):
    return {k: getattr(p, k) for k in PROFILE_KEYS}


def get_profile(user: User, db: Session) -> FinancialProfile:
    p = user.profile
    if not p:
        p = FinancialProfile(user_id=user.id)
        db.add(p); db.commit(); db.refresh(p)
    return p


def record_score(db: Session, user_id: int, score: int):
    last = (db.query(ScoreHistory).filter_by(user_id=user_id)
            .order_by(ScoreHistory.id.desc()).first())
    if not last or last.score != score:
        db.add(ScoreHistory(user_id=user_id, score=score))


# ---------- Auth ----------
@app.post("/api/auth/register", response_model=TokenOut, status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=data.email.lower()).first():
        raise HTTPException(409, "Email already registered")
    u = User(name=data.name, email=data.email.lower(), password_hash=hash_password(data.password))
    db.add(u); db.commit(); db.refresh(u)
    db.add(FinancialProfile(user_id=u.id)); db.commit()
    return TokenOut(access_token=create_token(u.id))


@app.post("/api/auth/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    u = db.query(User).filter_by(email=data.email.lower()).first()
    if not u or not verify_password(data.password, u.password_hash):
        raise HTTPException(401, "Incorrect email or password")
    return TokenOut(access_token=create_token(u.id))


@app.get("/api/auth/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "name": user.name, "email": user.email}


# Logout is stateless: the client discards its token.
@app.post("/api/auth/logout")
def logout(user: User = Depends(current_user)):
    return {"detail": "Logged out"}


# ---------- Profile & scores ----------
@app.get("/api/profile")
def read_profile(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return profile_dict(get_profile(user, db))


@app.put("/api/profile")
def update_profile(data: ProfileIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if data.credit_used > data.credit_limit:
        raise HTTPException(422, "Credit used cannot exceed credit limit")
    p = get_profile(user, db)
    for k, v in data.model_dump().items():
        setattr(p, k, v)
    record_score(db, user.id, p.cibil_score)
    db.commit()
    return profile_dict(p)


@app.post("/api/scores", status_code=201)
def add_score(data: ScoreIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    p = get_profile(user, db)
    p.cibil_score = data.score
    db.add(ScoreHistory(user_id=user.id, score=data.score))
    db.commit()
    return {"score": data.score}


@app.get("/api/scores")
def score_history(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.query(ScoreHistory).filter_by(user_id=user.id).order_by(ScoreHistory.id).all()
    return [{"score": r.score, "date": r.recorded_at.strftime("%d %b %Y")} for r in rows]


# ---------- Dashboard ----------
@app.get("/api/dashboard")
def dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)):
    p = get_profile(user, db)
    m = analytics.compute_metrics(p)
    hist = db.query(ScoreHistory).filter_by(user_id=user.id).order_by(ScoreHistory.id).all()
    improvement = hist[-1].score - hist[0].score if len(hist) > 1 else 0
    rec = (db.query(Recommendation).filter_by(user_id=user.id, kind="analysis")
           .order_by(Recommendation.id.desc()).first())
    return {
        "user": {"name": user.name},
        "profile": profile_dict(p),
        "metrics": m,
        "improvement": improvement,
        "history": [{"score": h.score, "date": h.recorded_at.strftime("%d %b %Y")} for h in hist],
        "utilization_chart": [
            {"name": "Used", "value": p.credit_used},
            {"name": "Available", "value": max(p.credit_limit - p.credit_used, 0)},
        ],
        "latest_recommendation": rec.content if rec else None,
    }


# ---------- AI advisor ----------
@app.post("/api/advisor/analyze")
def advisor_analyze(user: User = Depends(current_user), db: Session = Depends(get_db)):
    p = get_profile(user, db)
    text = ai_service.analyze(p, analytics.compute_metrics(p))
    db.add(Recommendation(user_id=user.id, kind="analysis", content=text)); db.commit()
    return {"content": text}


@app.post("/api/advisor/chat")
def advisor_chat(data: ChatIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    p = get_profile(user, db)
    text = ai_service.chat(p, analytics.compute_metrics(p), data.message)
    db.add(Recommendation(user_id=user.id, kind="chat", prompt=data.message, content=text)); db.commit()
    return {"content": text}


@app.get("/api/recommendations")
def recommendations(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = (db.query(Recommendation).filter_by(user_id=user.id)
            .order_by(Recommendation.id.desc()).limit(20).all())
    return [{"kind": r.kind, "prompt": r.prompt, "content": r.content,
             "date": r.created_at.strftime("%d %b %Y %H:%M")} for r in rows]


@app.get("/api/health")
def health():
    return {"status": "ok"}
