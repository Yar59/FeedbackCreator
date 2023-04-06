import logging
import os
from enum import Enum, auto
from textwrap import dedent

from environs import Env
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler,
)

from main import read_excel, generate_feedback, save_feedback

logger = logging.getLogger(__name__)


class States(Enum):
    start = auto()
    handle_menu = auto()
    handle_file = auto()
    handle_link = auto()


class Transitions(Enum):
    menu = auto()
    generate_from_file = auto()
    get_template = auto()
    generate_by_link = auto()


def start(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton('Сгенерировать ОС из файла', callback_data=str(Transitions.generate_from_file))],
        [InlineKeyboardButton('Сгенерировать ОС по ссылке', callback_data=str(Transitions.generate_by_link))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if query:
        query.answer()
        query.message.reply_text(
            text='Привет, это бот, который умеет генерировать ОС на учеников:',
            reply_markup=reply_markup
        )
        query.message.delete()
    else:
        update.message.reply_text(
            text='Привет, это бот, который умеет генерировать ОС на учеников:',
            reply_markup=reply_markup
        )
    return States.handle_menu


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Пока-пока!'
    )

    return ConversationHandler.END


def send_template(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton('В меню', callback_data=str(Transitions.menu))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    with open("feedback.xlsx", "rb") as file:
        feedback_template = file.read()
    query.answer()
    query.message.reply_document(
        feedback_template,
        filename='feedback_template.xlsx',
        caption=dedent('''
            - Заполнить таблицу `feedback_template.xlsx` данными:
            - `ФИО` - ФИО ученика, необязательно
            - `Имя для ОС` - имя, которое будет записано в ОС, обязательно
            - `Текущий модуль` - выбрать модуль из списка доступных, необязательно, если используется ссылка
            - `Текущий урок` - номер урока модуля, необязательно, если используется ссылка
            - `Статус урока` - В работе или Сдается, необязательно, если используется ссылка
            - `Ссылка на девман` - ссылка на профиль ученика, необязательно
            
            После того как заполнишь файл, отправь его мне'''),
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )
    query.message.delete()
    return States.handle_file


def wait_for_file(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton('В меню', callback_data=str(Transitions.menu))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.answer()
    query.message.reply_text(
        text=dedent('''
            - Заполнить таблицу `feedback_template.xlsx` данными:
            - `ФИО` - ФИО ученика, необязательно
            - `Имя для ОС` - имя, которое будет записано в ОС, обязательно
            - `Текущий модуль` - выбрать модуль из списка доступных, необязательно, если используется ссылка
            - `Текущий урок` - номер урока модуля, необязательно, если используется ссылка
            - `Статус урока` - В работе или Сдается, необязательно, если используется ссылка
            - `Ссылка на девман` - ссылка на профиль ученика, необязательно

            После того как заполнишь файл, отправь его мне'''),
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )
    query.message.delete()
    return States.handle_file


def handle_file(update: Update, context: CallbackContext) -> int:
    chat_id = update.effective_chat.id
    os.makedirs('user_files', exist_ok=True)
    filename = f'{chat_id}feedback.xlsx'
    file_path = os.path.join('user_files', filename)
    with open(file_path, 'wb') as f:
        context.bot.get_file(update.message.document).download(out=f)

    students = read_excel(file_path)
    feedbacks = []
    for student in students:
        feedback = generate_feedback(student)
        feedbacks.append(feedback)
    save_feedback(file_path, feedbacks)

    with open(file_path, "rb") as file:
        user_feedback = file.read()
    keyboard = [
        [InlineKeyboardButton('В меню', callback_data=str(Transitions.menu))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_document(
        user_feedback,
        filename='feedback.xlsx',
        caption='ОС сгенерирована:',
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )
    return States.handle_file


def generate_from_file(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton('У меня есть готовый файл', callback_data=str(Transitions.generate_from_file))],
        [InlineKeyboardButton('Мне нужен шаблон', callback_data=str(Transitions.get_template))],
        [InlineKeyboardButton('В меню', callback_data=str(Transitions.menu))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.answer()
    query.message.reply_text(
        text='Для создания ОС из файла нужна Excel табличка',
        reply_markup=reply_markup
    )
    query.message.delete()
    return States.handle_file


def wait_for_name(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton('В меню', callback_data=str(Transitions.menu))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.answer()
    query.message.reply_text(
        text='Как зовут ученика? (Имя будет использовано в ОС, отправь мне его текстом)',
        reply_markup=reply_markup
    )
    query.message.delete()
    return States.handle_link


def handle_name(update: Update, context: CallbackContext) -> int:
    student_name = update.message.text
    context.user_data["student_name"] = student_name
    keyboard = [
        [InlineKeyboardButton('В меню', callback_data=str(Transitions.menu))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        text='Теперь мне нужна ссылка на профиль ученика',
        reply_markup=reply_markup
    )
    return States.handle_link


def handle_link(update: Update, context: CallbackContext) -> int:
    student_link = update.message.text

    student = {
        'Ссылка на девман': student_link,
        'Имя для ОС': context.user_data["student_name"],
    }
    feedback = generate_feedback(student)
    keyboard = [
        [InlineKeyboardButton('В меню', callback_data=str(Transitions.menu))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        text=f'Ос на ученика:\n{feedback}',
        reply_markup=reply_markup
    )
    return States.handle_link


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    env = Env()
    env.read_env()
    tg_token = env('TG_TOKEN')

    updater = Updater(token=tg_token)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
        ],
        states={
            States.handle_menu: [
                CallbackQueryHandler(generate_from_file, pattern=f'^{Transitions.generate_from_file}$'),
                CallbackQueryHandler(wait_for_name, pattern=f'^{Transitions.generate_by_link}$'),
            ],
            States.handle_file: [
                CallbackQueryHandler(start, pattern=f'^{Transitions.menu}$'),
                CallbackQueryHandler(send_template, pattern=f'^{Transitions.get_template}$'),
                CallbackQueryHandler(wait_for_file, pattern=f'^{Transitions.generate_from_file}$'),
                MessageHandler(Filters.document, handle_file),
            ],
            States.handle_link: [
                CallbackQueryHandler(start, pattern=f'^{Transitions.menu}$'),
                MessageHandler(Filters.entity('url'), handle_link),
                MessageHandler(Filters.text, handle_name),
            ]
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('start', cancel),
        ],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
