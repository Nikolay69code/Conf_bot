from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, and_, or_
from models import Base, User, Category, SpecificItem
import json
import logging
from typing import List, Dict, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Словарь соответствия категорий и их русских названий
CATEGORY_TRANSLATIONS = {
    'food': 'Продукты питания',
    'clothes': 'Одежда',
    'medicine': 'Медикаменты',
    'electronics': 'Техника',
    'other': 'Другое'
}

# Обратный словарь для перевода с русского на английский
REVERSE_CATEGORY_TRANSLATIONS = {v: k for k, v in CATEGORY_TRANSLATIONS.items()}

app = FastAPI()

# Настройка базы данных
DATABASE_URL = "sqlite+aiosqlite:///bot.db"
engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

async def get_or_create_category(session: AsyncSession, category_name: str) -> Category:
    """Получает или создает категорию"""
    # Если пришло русское название, переводим его в английский ключ
    if category_name in REVERSE_CATEGORY_TRANSLATIONS:
        category_name = REVERSE_CATEGORY_TRANSLATIONS[category_name]
    
    stmt = select(Category).where(Category.name == category_name)
    result = await session.execute(stmt)
    category = result.scalar_one_or_none()
    
    if not category:
        category = Category(name=category_name)
        session.add(category)
        await session.flush()
    
    return category

async def create_specific_items(session: AsyncSession, user: User, items_data: List[Dict[str, Any]]):
    """Создает конкретные вещи для пользователя"""
    for item_data in items_data:
        category = None
        if item_data.get('category'):
            category = await get_or_create_category(session, item_data['category'])
        
        item = SpecificItem(
            user=user,
            name=item_data['name'],
            description=item_data.get('description'),
            quantity=item_data.get('quantity'),
            category=category
        )
        session.add(item)

def translate_category(category_name: str) -> str:
    """Переводит название категории на русский язык"""
    return CATEGORY_TRANSLATIONS.get(category_name, category_name)

async def find_matches(user: User, session: AsyncSession) -> List[Dict[str, Any]]:
    """Находит совпадения по категориям и конкретным вещам"""
    # Получаем все категории пользователя
    user_categories = [cat.name for cat in user.categories]
    
    # Получаем все конкретные вещи пользователя
    user_items = [item.name.lower() for item in user.specific_items]
    
    # Ищем пользователей с противоположным типом
    opposite_type = 'volunteer' if user.user_type == 'military' else 'military'
    
    # Базовый запрос для поиска пользователей
    stmt = select(User).where(User.user_type == opposite_type)
    result = await session.execute(stmt)
    potential_matches = result.scalars().all()
    
    matches = []
    for potential_match in potential_matches:
        match_score = 0
        match_details = {
            'user': {
                'full_name': potential_match.full_name,
                'organization_name': potential_match.organization_name,
                'contact_person': potential_match.contact_person,
                'phone': potential_match.phone
            },
            'matching_categories': [],
            'matching_items': []
        }
        
        # Проверяем совпадения по категориям
        for category in potential_match.categories:
            if category.name in user_categories:
                match_score += 1
                # Добавляем русское название категории
                match_details['matching_categories'].append(translate_category(category.name))
        
        # Проверяем совпадения по конкретным вещам
        for item in potential_match.specific_items:
            if item.name.lower() in user_items:
                match_score += 2
                match_details['matching_items'].append({
                    'name': item.name,
                    'description': item.description,
                    'quantity': item.quantity,
                    'category': translate_category(item.category.name) if item.category else None
                })
        
        if match_score > 0:
            match_details['match_score'] = match_score
            matches.append(match_details)
    
    # Сортируем совпадения по score
    matches.sort(key=lambda x: x['match_score'], reverse=True)
    return matches

@app.post("/submit")
async def submit_data(request: Request):
    try:
        data = await request.json()
        
        # Создаем новую сессию
        async with async_session() as session:
            # Создаем нового пользователя
            user = User(
                telegram_id=data.get("telegram_id"),
                full_name=data.get("fullName"),
                phone=data.get("phone"),
                organization_type=data.get("orgType"),
                organization_name=data.get("orgName"),
                contact_person=data.get("contactPerson"),
                website=data.get("website"),
                user_type=data.get("userType")
            )
            
            # Добавляем пользователя в базу данных
            session.add(user)
            await session.flush()
            
            # Добавляем категории
            for category_name in data.get("categories", []):
                category = await get_or_create_category(session, category_name)
                user.categories.append(category)
            
            # Добавляем конкретные вещи
            await create_specific_items(session, user, data.get("specificItems", []))
            
            # Сохраняем изменения
            await session.commit()
            
            # Ищем совпадения
            matches = await find_matches(user, session)
            
            return {
                "status": "success",
                "matches": matches
            }
    except Exception as e:
        logger.error(f"Error processing submission: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 