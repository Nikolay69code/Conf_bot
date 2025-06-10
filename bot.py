import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import settings
from models import Base
from states import RegistrationStates
from keyboards import (
    get_user_type_keyboard,
    get_location_keyboard,
    get_help_categories_keyboard,
    get_confirmation_keyboard
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=settings.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Настройка базы данных
engine = create_async_engine(settings.DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Обработчики команд
@dp.message(commands=["start"])
async def cmd_start(message):
    await message.answer(
        "Добро пожаловать! Выберите вашу роль:",
        reply_markup=get_user_type_keyboard()
    )
    await dp.storage.set_state(user=message.from_user.id, state=RegistrationStates.choosing_type)

@dp.message(commands=["chatID"])
async def cmd_chat_id(message):
    await message.answer(f"ID этого чата: {message.chat.id}")

# Обработчики состояний
@dp.message(RegistrationStates.choosing_type)
async def process_user_type(message):
    if message.text not in ["Военный", "Волонтер"]:
        await message.answer("Пожалуйста, выберите один из предложенных вариантов")
        return
    
    await dp.storage.update_data(
        user=message.from_user.id,
        data={"user_type": message.text}
    )
    await message.answer("Введите ваше полное имя:")
    await dp.storage.set_state(user=message.from_user.id, state=RegistrationStates.full_name)

@dp.message(RegistrationStates.full_name)
async def process_full_name(message):
    await dp.storage.update_data(
        user=message.from_user.id,
        data={"full_name": message.text}
    )
    await message.answer("Введите ваш номер телефона:")
    await dp.storage.set_state(user=message.from_user.id, state=RegistrationStates.phone)

@dp.message(RegistrationStates.phone)
async def process_phone(message):
    await dp.storage.update_data(
        user=message.from_user.id,
        data={"phone": message.text}
    )
    await message.answer(
        "Отправьте вашу геолокацию:",
        reply_markup=get_location_keyboard()
    )
    await dp.storage.set_state(user=message.from_user.id, state=RegistrationStates.location)

# Обработчик геолокации
@dp.message(RegistrationStates.location, content_types=["location"])
async def process_location(message):
    await dp.storage.update_data(
        user=message.from_user.id,
        data={
            "latitude": message.location.latitude,
            "longitude": message.location.longitude
        }
    )
    await message.answer("Выберите категории помощи:", reply_markup=get_help_categories_keyboard())
    await dp.storage.set_state(user=message.from_user.id, state=RegistrationStates.help_categories)

async def notify_admin(military_user, volunteer):
    """Отправка уведомления администратору о совпадении"""
    try:
        message = f"Найдено совпадение!\n\nВоенный: {military_user.full_name}\nВолонтер: {volunteer.full_name}"
        await bot.send_message(settings.ADMIN_ID, message)
    except Exception as e:
        logger.error(f"Error sending notification to admin: {str(e)}")

async def main():
    # Инициализация базы данных
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 