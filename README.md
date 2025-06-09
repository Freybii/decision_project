# Проєкт Decision Project

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![GitHub Actions](https://img.shields.io/github/actions/workflow/status/Freybii/decision_project/django.yml?branch=main)](https://github.com/Freybii/decision_project/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Потужний додаток для прийняття рішень на основі Django, який допомагає користувачам приймати обґрунтовані рішення через структурований аналіз та порівняння альтернатив. Додаток надає комплексний набір інструментів для керування проєктами, порівняння альтернатив та аналізу рішень.

## 👤 Автор

- **ПІБ**: Дзірба Б. П.
- **Група**: ФеП-41
- **Керівник**: Катеринчук Іван Миколайович к.ф.-м.н., доцент
- **Дата виконання**: [31.05.2025]

## 🌟 Можливості

### 🔐 Система аутентифікації
- Кастомна модель користувача з аутентифікацією через email
- Інтеграція Google OAuth для зручного входу
- Захищена обробка паролів та JWT-токени
- Керування профілем користувача з підтримкою аватарів

### 📊 Аналіз рішень
- Створення та керування проєктами рішень
- Додавання та порівняння альтернатив
- Оцінювання альтернатив на основі критеріїв
- Візуалізація зв'язків між рішеннями
- Мережевий аналіз складних рішень з використанням NetworkX

### 🎯 Керування проєктами
- Створення та організація проєктів рішень
- Додавання детальних описів та критеріїв
- Завантаження зображень проєктів
- Відстеження прогресу проєкту
- Спільне прийняття рішень

### 💡 Керування альтернативами
- Додавання кількох альтернатив до проєктів
- Визначення зв'язків між альтернативами
- Оцінювання альтернатив на основі критеріїв
- Візуальне порівняння альтернатив
- Експорт результатів аналізу

### 🔄 Інтеграція API
- RESTful API ендпоінти
- Аутентифікація через JWT
- Серіалізовані відповіді даних
- Детальна документація API
- Підтримка Swagger/OpenAPI

## 🛠 Технологічний стек

- **Бекенд-фреймворк**: [Django 4.2](https://www.djangoproject.com/)
- **REST-фреймворк**: [Django REST Framework 3.14](https://www.django-rest-framework.org/)
- **База даних**: [SQLite](https://www.SQLite.org/)
- **Аутентифікація**: JWT, Google OAuth
- **Фронтенд**: Django Templates, [Bootstrap 5](https://getbootstrap.com/)
- **Аналіз**: [NetworkX](https://networkx.org/) для мережевого аналізу
- **Тестування**: Django Test Framework
- **CI/CD**: GitHub Actions

## 📋 Передумови

- Python 3.9+
- SQLite
- Віртуальне середовище (рекомендовано)
- Облікові дані Google OAuth (для входу через Google)

## 🚀 Встановлення

1. Клонуйте репозиторій:
   ```bash
   git clone https://github.com/Freybii/decision_project.git
   cd decision_project
   ```

2. Створіть та активуйте віртуальне середовище:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Встановіть залежності:
   ```bash
   pip install -r requirements.txt
   ```

4. Налаштуйте змінні середовища:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Виконайте міграції:
   ```bash
   python manage.py migrate
   ```

6. Створіть суперкористувача:
   ```bash
   python manage.py createsuperuser
   ```

7. Запустіть сервер розробки:
   ```bash
   python manage.py runserver
   ```

## 📁 Project Structure

```
decision_project/
├── authentication/     # Аутентифікація та керування користувачами
├── main/              # Основна функціональність прийняття рішень
├── decisionproject/   # Конфігурація проєкту
├── media/            # Файли, завантажені користувачами
├── .github/          # GitHub Actions workflows
└── requirements.txt  # Залежності проєкту
```

## 🔌 API Ендпоінти

### Аутентифікація
- `POST /api/auth/register/` - Реєстрація користувача
- `POST /api/auth/login/` - Вхід користувача
- `POST /api/auth/google-login/` - Вхід через Google OAuth
- `GET /api/auth/profile/` - Профіль користувача
- `PUT /api/auth/profile/` - Оновлення профілю

### Проєкти
- `GET /api/projects/` - Список проєктів
- `POST /api/projects/` - Створення проєкту
- `GET /api/projects/{id}/` - Деталі проєкту
- `PUT /api/projects/{id}/` - Оновлення проєкту
- `DELETE /api/projects/{id}/` - Видалення проєкту

### Альтернативи
- `GET /api/projects/{id}/alternatives/` - Список альтернатив
- `POST /api/projects/{id}/alternatives/` - Додати альтернативу
- `GET /api/alternatives/{id}/` - Деталі альтернативи
- `PUT /api/alternatives/{id}/` - Оновити альтернативу
- `DELETE /api/alternatives/{id}/` - Видалити альтернативу

## 🤝 Участь у розробці

1. Форкніть репозиторій
2. Створіть гілку для функціоналу: `git checkout -b feature/your-feature`
3. Зробіть коміт змін: `git commit -am 'Add your feature'`
4. Запуште гілку: `git push origin feature/your-feature`
5. Створіть pull request

## 🧪 Тестування

Запустіть тести:
```bash
python manage.py test
```

## 📝 Стиль коду

Проєкт дотримується стилю PEP 8. Запустіть лінтер:
```bash
flake8 .
```

## 💬 Підтримка

For support, please:
- Відкрийте issue у репозиторії GitHub
- Зв'яжіться з мейнтейнерами
- Приєднуйтесь до обговорень у спільноті

## 🙏 Подяки

- Спільноти [Django](https://www.djangoproject.com/) та [Django REST Framework](https://www.django-rest-framework.org/)
- [NetworkX](https://networkx.org/) за можливості мережевого аналізу

## 📞 Контакти

- GitHub: [@Freybii](https://github.com/Freybii)
- Посилання на проєкт: [https://github.com/Freybii/decision_project](https://github.com/Freybii/decision_project) 
