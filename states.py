from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    choosing_type = State()  # Выбор типа пользователя
    full_name = State()      # Ввод ФИО
    phone = State()          # Ввод телефона
    location = State()       # Ввод геолокации
    org_type = State()       # Тип организации
    org_name = State()       # Название организации
    contact_person = State() # Контактное лицо
    website = State()        # Сайт
    help_categories = State()# Категории помощи
    specific_items = State() # Конкретные вещи/продукты
    confirmation = State()   # Подтверждение данных 