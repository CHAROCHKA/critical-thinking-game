from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import redis
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db, engine, Base
from models import Headline, Answer, GameSession, User
from schemas import HeadlineOut, AnswerIn, AnswerOut, StatsOut
import random
import json

app = FastAPI()

# Монтируем статику на /static
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Корневой путь отдаёт index.html
@app.get("/")
async def root():
    return FileResponse("static/index.html")

# Redis client
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/ping")
async def ping():
    try:
        redis_client.ping()
        redis_status = "ok"
    except:
        redis_status = "fail"
    return {
        "redis": redis_status,
        "postgres": "not checked"
    }

@app.get("/game/next", response_model=HeadlineOut)
async def get_next_headline(db: AsyncSession = Depends(get_db)):
    # Проверяем кэш
    cached = redis_client.lpop("headlines_pool")
    if cached:
        headline_data = json.loads(cached)
        return HeadlineOut(**headline_data)
    
    result = await db.execute(select(Headline))
    headlines = result.scalars().all()
    if not headlines:
        raise HTTPException(status_code=404, detail="No headlines available")
    
    chosen = random.choice(headlines)
    
    pool = random.sample(headlines, min(20, len(headlines)))
    for h in pool:
        redis_client.rpush("headlines_pool", json.dumps({
            "id": h.id,
            "text": h.text,
            "is_manipulative": h.is_manipulative,
            "category": h.category,
            "difficulty": h.difficulty
        }))
    
    return HeadlineOut(
        id=chosen.id,
        text=chosen.text,
        is_manipulative=chosen.is_manipulative,
        category=chosen.category,
        difficulty=chosen.difficulty
    )

@app.post("/game/answer", response_model=AnswerOut)
async def submit_answer(answer: AnswerIn, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Headline).where(Headline.id == answer.headline_id))
    headline = result.scalar_one_or_none()
    if not headline:
        raise HTTPException(status_code=404, detail="Headline not found")
    
    is_correct = (answer.user_answer == headline.is_manipulative)
    
    new_answer = Answer(
        user_id=1,
        headline_id=headline.id,
        user_answer=answer.user_answer,
        is_correct=is_correct
    )
    db.add(new_answer)
    await db.commit()
    
    return AnswerOut(
        is_correct=is_correct,
        correct_answer=headline.is_manipulative,
        explanation="Объяснение будет добавлено позже"
    )

@app.get("/game/stats", response_model=StatsOut)
async def get_stats(db: AsyncSession = Depends(get_db)):
    total = await db.scalar(select(func.count(Answer.id)))
    correct = await db.scalar(select(func.count(Answer.id)).where(Answer.is_correct == True))
    return StatsOut(
        total_answers=total or 0,
        correct_answers=correct or 0,
        score=0,
        level=1
    )
