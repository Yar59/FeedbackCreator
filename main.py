import argparse
import logging
import random
from textwrap import dedent
from time import sleep

import pandas
import requests
from num2words import num2words

from modules_knowledge import MODULES_KNOWLEDGE
from dvmn_parser import get_student_page, get_lesson

PHRASES = {
    'knowledge_statuses': {
        'in_work': [
            'изучает',
            'проходит',
            'осваивает',
            'освоит',
            'изучит',
            'пройдет',
        ],
        'completed': [
            'изучил',
            'прошел',
            'освоил',
        ],
    },
    'at_lesson': [
        'в ходе которого',
        'на протяжении которого',
        'в котором',
    ],
    'commendations': [
        'отлично справляется со всеми задачами',
        'самостоятельно анализирует и выполняет задачи',
        'полностью сконцентрирован на обучении',
    ]
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--manual_additions',
        help="Включить ввод дополнения во время работы скрипта",
        action='store_true'
    )
    parser.add_argument(
        '--dont_save',
        help="Не сохранять в файл",
        action='store_true'
    )
    parser.add_argument(
        '--dont_use_link',
        help="Не сохранять в файл",
        action='store_true'
    )

    args = parser.parse_args()
    manual_additions = args.manual_additions
    dont_save = args.dont_save
    dont_use_link = args.dont_use_link
    students = pandas.read_excel(
        'feedback.xlsx',
        sheet_name='feedback',
        usecols=[
            'ФИО',
            'Имя для ОС',
            'Текущий модуль',
            'Текущий урок',
            'Статус урока',
            'Ссылка на девман'
        ],
    ).to_dict(orient='records')

    feedbacks = []
    for student in students:
        if student['Ссылка на девман'] and not dont_use_link:
            print(student['Ссылка на девман'])
            while True:
                try:
                    page_content = get_student_page(student['Ссылка на девман'])
                    lesson = get_lesson(page_content)
                    lesson_status = lesson['lesson_status']
                    module_name = lesson['module_name']
                    lesson_number_numerical = int(lesson['lesson_number'])
                    break
                except requests.exceptions.HTTPError as error:
                    logging.warning(error)
                    break
                except requests.exceptions.ConnectionError:
                    logging.warning("Connection Error\nPlease check your internet connection")
                    sleep(5)
                    logging.warning("Trying to reconnect")
        else:
            lesson_status = student['Статус урока']
            module_name = student['Текущий модуль']
            lesson_number_numerical = student["Текущий урок"]
        lesson_number = num2words(lesson_number_numerical, to="ordinal", lang="ru")
        try:
            module_knowledge = random.choice(MODULES_KNOWLEDGE[module_name][lesson_number_numerical])
            commendation = random.choice(PHRASES['commendations'])
            if lesson_status == 'В работе':
                work_status = 'сейчас выполняет'
                knowledge_status = random.choice(PHRASES['knowledge_statuses']['in_work'])
            elif lesson_status == 'Сдается':
                work_status = 'сейчас сдает'
                knowledge_status = random.choice(PHRASES['knowledge_statuses']['completed'])
            else:
                work_status = 'недавно сдал'
                knowledge_status = random.choice(PHRASES['knowledge_statuses']['completed'])
            feedback = dedent(f'''\
                {student["Имя для ОС"]} {work_status} {lesson_number} проект модуля {module_name} 
                в ходе которого {knowledge_status} {module_knowledge}. На занятиях {commendation}.
            ''')
            print(feedback)

            if manual_additions:
                additions = input('Чем дополним ОС?\n')
                feedback += additions
                print(feedback, '\n')

            feedbacks.append(feedback.replace('\n', ' '))
        except KeyError:
            print(f'Модуля {module_name} нет в скрипте, ОС по {student["ФИО"]} не сгенерирована')
            feedbacks.append('Текущего модуля нет в скрипте')

    if not dont_save:
        writer = pandas.ExcelWriter('feedback.xlsx', engine='openpyxl', mode='a', if_sheet_exists='overlay')
        wb = writer.book
        data_frame = pandas.DataFrame({'ОС': feedbacks})
        data_frame.to_excel(writer, sheet_name='feedback', index=False, startcol=6)
        wb.save('feedback.xlsx')


if __name__ == '__main__':
    main()
