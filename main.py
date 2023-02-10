import argparse
import random
from textwrap import dedent

import pandas
from num2words import num2words

from modules_knowledge import MODULES_KNOWLEDGE

PHRASES = {
    'knowledge_statuses': {
        'in_work': [
            'изучает',
            'проходит',
            'осваивает',
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

    args = parser.parse_args()
    manual_additions = args.manual_additions
    dont_save = args.dont_save
    students = pandas.read_excel(
        'feedback.xlsx',
        sheet_name='feedback',
        usecols=[
            'ФИО',
            'Имя для ОС',
            'Текущий модуль',
            'Текущий урок',
            'Статус урока',
        ],
    ).to_dict(orient='records')

    feedbacks = []
    for student in students:
        lesson_status = student['Статус урока']
        module_name = student['Текущий модуль']
        lesson_number_numerical = student["Текущий урок"]
        lesson_number = num2words(lesson_number_numerical, to="ordinal", lang="ru")
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

    if not dont_save:
        writer = pandas.ExcelWriter('feedback.xlsx', engine='openpyxl', mode='a', if_sheet_exists='overlay')
        wb = writer.book
        data_frame = pandas.DataFrame({'ОС': feedbacks})
        data_frame.to_excel(writer, sheet_name='feedback', index=False, startcol=6)
        wb.save('feedback.xlsx')


if __name__ == '__main__':
    main()
