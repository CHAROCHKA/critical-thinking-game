import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from models import Headline
from database import DATABASE_URL, engine, Base, AsyncSessionLocal

HEADLINES = [
    {"text": "Учёные доказали, что кофе вызывает рак", "is_manipulative": True, "category": "страх", "difficulty": 1},
    {"text": "Власти скрывают правду о новом налоге", "is_manipulative": True, "category": "недоверие", "difficulty": 2},
    {"text": "Продажи автомобилей выросли на 10% за год", "is_manipulative": False, "category": None, "difficulty": 1},
    {"text": "Зарплаты бюджетников повысят в следующем году", "is_manipulative": False, "category": None, "difficulty": 1},
    {"text": "Срочно! Курс доллара рухнул!", "is_manipulative": True, "category": "страх", "difficulty": 2},
    {"text": "Правительство решило отменить пенсии", "is_manipulative": True, "category": "страх", "difficulty": 3},
    {"text": "Новый закон улучшит жизнь пенсионеров", "is_manipulative": False, "category": None, "difficulty": 1},
    {"text": "Секретные документы стали доступны", "is_manipulative": True, "category": "сенсация", "difficulty": 2},
    {"text": "Безопасность ваших данных под угрозой", "is_manipulative": True, "category": "страх", "difficulty": 2},
    {"text": "Компания Х объявила о рекордной прибыли", "is_manipulative": False, "category": None, "difficulty": 1},
]

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # Проверяем, есть ли данные
        from sqlalchemy import select
        result = await session.execute(select(Headline))
        existing = result.scalars().first()
        if existing:
            print("Данные уже есть, пропускаем.")
            return
        
        for h in HEADLINES:
            session.add(Headline(**h))
        await session.commit()
        print(f"Добавлено {len(HEADLINES)} заголовков.")

if __name__ == "__main__":
    asyncio.run(seed())
