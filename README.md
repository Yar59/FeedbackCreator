# Генератор обратной связи по ученикам школы "Третье Место"
Скрипт генерирует обратную связь(ОС) по ученикам исходя из их текущего прогресса.

Также имеется телеграмм-бот, позволяющий не разворачивать проект у себя. Доступен по [ссылке](https://t.me/third_place_feedback_bot).

Нацелен на создание заготовки для обратной связи, которую в дальнейшем необходимо дополнить чем-то индивидуальным.

Формат ОС:
1. Имя ученика
2. Текущий прогресс ученика
3. Похвала
4. Дополнение преподавателя
## Установка
Python 3.9+ должен быть установлен

Для установки зависимостей используйте
```commandline
pip install -r requirements.txt
```

Для использования бота создайте файл `.env` в директории проекта и запишите в него токен бота в виде
```
TG_TOKEN=токен вашего бота
```

## Использование
- Скачать и установить проект
- Заполнить таблицу `feedback.xlsx` данными:
  - `ФИО` - ФИО ученика, необязательно
  - `Имя для ОС` - имя, которое будет записано в ОС, обязательно
  - `Текущий модуль` - выбрать модуль из списка доступных, необязательно, если используется ссылка
  - `Текущий урок` - номер урока модуля, необязательно, если используется ссылка
  - `Статус урока` - В работе или Сдается, необязательно, если используется ссылка
  - `Ссылка на девман` - ссылка на профиль ученика, необязательно
- Запустить скрипт `main.py`
- Наслаждаться жизнью

Доступные аргументы:
- `--manual_additions` - ввод дополнений к ОС прямо во время работы скрипта
- `--dont_save` - отключить сохранение ОС в файл
- `--dont_use_link` - отключить парсинг уроков с девмана по ссылке

Пример запуска:
```commandline
python main.py --manual_additions --dont_save
```
Запустит скрипт генерации ОС с вводом дополнений к ОС без сохранения изменений в файл


Для запуска бота используйте команду:
```commandline
python tg-bot.py
```
## Индивидуализация
Знания полученные учеником в ходе проекта можно дополнить или отредактировать в файле `modules_knowledge.py`

Некоторые фразы, используемые при создании ОС находятся в глобальной переменной `PHRASES` внутри файла `main.py`

## В планах
1) Учитывать пол ребенка
2) Добавить ОС по нескольким урокам ордновременно
3) Добавить загрузку ОС в хо-хо

Буду благодарен любой помощи в улучшении скрипта