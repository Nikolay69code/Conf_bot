from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_user_type_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Военный")],
            [KeyboardButton(text="Волонтер")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_location_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить геолокацию", request_location=True)]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_help_categories_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Продукты питания", callback_data="food")],
            [InlineKeyboardButton(text="Одежда", callback_data="clothes")],
            [InlineKeyboardButton(text="Медикаменты", callback_data="medicine")],
            [InlineKeyboardButton(text="Техника", callback_data="electronics")],
            [InlineKeyboardButton(text="Другое", callback_data="other")]
        ]
    )
    return keyboard

def get_confirmation_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Подтвердить", callback_data="confirm")],
            [InlineKeyboardButton(text="Начать заново", callback_data="restart")]
        ]
    )
    return keyboard 