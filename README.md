## Motobinfile :motorcycle:

[Motobinfile](https://motobinfile.com) — интернет-магазин по продаже программного обеспечения для программирования блоков управления мотоциклами. Он предоставляет пользователям возможность искать, просматривать, добавлять товары в корзину и совершать интернет-платежи. Я решил использовать новый стек технологий, с которыми раньше не работал, включая Flask, Postgres, SQLAlchemy и Stripe. Также добавил Telegram Bot, который отправляет уведомления о новых покупках с помощью TelegramBotApi. Этот проект был разработан, чтобы помочь любителям мотоциклов найти и приобрести программное обеспечение для программирования блоков управления своих мотоциклов.

### Как развернуть проект: :question:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Artem4es/motobinfile.git
```

```
cd motobinfile
```

Cоздать и активировать виртуальное окружение:

```
python3.10 -m venv venv
```

```
source venv/Scripts/activate (venv/bin/activate для МасOS, Linux)
```

```
python3 -m pip install --upgrade pip (python далее везде для Windows)
```

Установить зависимости из requirements.txt:

```
pip install -r requirements.txt
```

Cоздать файл c переменными окружения .env в папке с проектом вида:
```
STRIPE_KEY = Ключ от Stripe API
FLASK_KEY = Пароль от Flask
TELEGRAM_TOKEN = Токен телеграм бота для оповещений о заказах
ADMIN_ID = Ваш ID в Telegram
PSGL_PASS = Пароль от БД
PRICE_30 = Пароль от продукта
PRICE_50 = Пароль от другого продукта
RECAPTCHA_PUBLIC_KEY = Google recaptcha key
RECAPTCHA_PRIVATE_KEY=
```

Выполнить миграции:

```
flask db init
flask db migrate -m "имя базовой миграции"
flask db upgrade
```

Если возникает ошибка 'no Flask app...':
```export FLASK_APP=main.py```

Запустить проект:

```
python3 main.py
```

## Планы по улучшению проекта: :rocket:

- Нормализация базы данных для повышения производительности
- Внедрение шаблона проектирования Blueprint для лучшей организации кода

