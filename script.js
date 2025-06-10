let tg = window.Telegram.WebApp;
let formData = {
    userType: '',
    fullName: '',
    phone: '',
    orgType: '',
    orgName: '',
    contactPerson: '',
    website: '',
    categories: [],
    specificItems: ''
};

// Словарь соответствия категорий
const CATEGORY_MAPPING = {
    'Продукты питания': 'food',
    'Одежда': 'clothes',
    'Медикаменты': 'medicine',
    'Техника': 'electronics',
    'Другое': 'other'
};

// Обратный словарь для отображения
const REVERSE_CATEGORY_MAPPING = {
    'food': 'Продукты питания',
    'clothes': 'Одежда',
    'medicine': 'Медикаменты',
    'electronics': 'Техника',
    'other': 'Другое'
};

// Инициализация приложения
tg.expand();
tg.enableClosingConfirmation();

// Функции для работы с формами
function showStep(stepNumber) {
    document.querySelectorAll('.form-step').forEach(step => {
        step.classList.add('hidden');
    });
    document.getElementById(`step-${stepNumber}`).classList.remove('hidden');
}

function selectUserType(type) {
    formData.userType = type;
    showStep(2);
}

// Валидация и форматирование телефона
function formatPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length > 0) {
        value = '+7 (' + value.substring(1, 4) + ') ' + value.substring(4, 7) + '-' + value.substring(7, 9) + '-' + value.substring(9, 11);
    }
    input.value = value;
}

// Валидация ФИО
function validateFullName(input) {
    const regex = /^[А-Яа-яЁё\s-]{2,100}$/;
    return regex.test(input.value);
}

// Валидация телефона
function validatePhone(input) {
    const regex = /^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$/;
    return regex.test(input.value);
}

// Валидация URL
function validateUrl(input) {
    if (!input.value) return true; // URL не обязателен
    const regex = /^https?:\/\/.+/;
    return regex.test(input.value);
}

function validatePersonalInfo() {
    const fullNameInput = document.getElementById('fullName');
    const phoneInput = document.getElementById('phone');
    
    if (!validateFullName(fullNameInput)) {
        fullNameInput.focus();
        return;
    }
    
    if (!validatePhone(phoneInput)) {
        phoneInput.focus();
        return;
    }
    
    formData.fullName = fullNameInput.value;
    formData.phone = phoneInput.value;
    showStep(3);
}

function validateOrgInfo() {
    const orgTypeInput = document.getElementById('orgType');
    const orgNameInput = document.getElementById('orgName');
    const contactPersonInput = document.getElementById('contactPerson');
    const websiteInput = document.getElementById('website');
    
    if (!orgTypeInput.value) {
        orgTypeInput.focus();
        return;
    }
    
    if (!orgNameInput.value) {
        orgNameInput.focus();
        return;
    }
    
    if (!contactPersonInput.value) {
        contactPersonInput.focus();
        return;
    }
    
    if (!validateUrl(websiteInput)) {
        websiteInput.focus();
        return;
    }
    
    formData.orgType = orgTypeInput.value;
    formData.orgName = orgNameInput.value;
    formData.contactPerson = contactPersonInput.value;
    formData.website = websiteInput.value;
    showStep(4);
}

function validateCategories() {
    if (formData.categories.length === 0) {
        alert('Пожалуйста, выберите хотя бы одну категорию помощи');
        return;
    }
    showStep(5);
}

function validateSpecificItems() {
    const specificItemsInput = document.getElementById('specificItems');
    if (!specificItemsInput.value.trim()) {
        specificItemsInput.focus();
        return;
    }
    formData.specificItems = specificItemsInput.value;
    showConfirmation();
}

function toggleCategory(category) {
    const button = document.querySelector(`[onclick="toggleCategory('${category}')"]`);
    const index = formData.categories.indexOf(category);
    
    if (index === -1) {
        formData.categories.push(category);
        button.classList.add('selected');
    } else {
        formData.categories.splice(index, 1);
        button.classList.remove('selected');
    }
}

function showConfirmation() {
    const confirmationData = document.getElementById('confirmation-data');
    
    confirmationData.innerHTML = `
        <p><strong>Тип пользователя:</strong> ${formData.userType === 'military' ? 'Военный' : 'Волонтер'}</p>
        <p><strong>ФИО:</strong> ${formData.fullName}</p>
        <p><strong>Телефон:</strong> ${formData.phone}</p>
        <p><strong>Тип организации:</strong> ${formData.orgType}</p>
        <p><strong>Название организации:</strong> ${formData.orgName}</p>
        <p><strong>Контактное лицо:</strong> ${formData.contactPerson}</p>
        <p><strong>Сайт:</strong> ${formData.website}</p>
        <p><strong>Категории помощи:</strong> ${formData.categories.join(', ')}</p>
        <p><strong>Конкретные вещи/продукты:</strong> ${formData.specificItems}</p>
    `;
    showStep(6);
}

function submitForm() {
    // Преобразуем русские названия категорий в английские перед отправкой
    const dataToSend = {
        ...formData,
        categories: formData.categories.map(category => CATEGORY_MAPPING[category])
    };
    tg.sendData(JSON.stringify(dataToSend));
    tg.close();
}

function restartForm() {
    formData = {
        userType: '',
        fullName: '',
        phone: '',
        orgType: '',
        orgName: '',
        contactPerson: '',
        website: '',
        categories: [],
        specificItems: ''
    };
    document.querySelectorAll('.category-btn').forEach(btn => btn.classList.remove('selected'));
    document.querySelectorAll('.input-field').forEach(input => input.value = '');
    showStep(1);
}

// Инициализация обработчиков событий
document.addEventListener('DOMContentLoaded', () => {
    const phoneInput = document.getElementById('phone');
    phoneInput.addEventListener('input', () => formatPhoneNumber(phoneInput));
});
