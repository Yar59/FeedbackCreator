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
        'Хорошо усваивает материал и может применять его на практике.',
        'Хорошо справляется с нагрузкой, получаемый материал хорошо запоминает и может им пользоваться в последующих проектах.',
        'Cамостоятельный, хорошо чувствует ход работы программ, которые пишет.',
        'Хорошо дружит с документацией, трудностей не возникает. Умеет правильно сформировать вопрос.',
        'Хорошо справляется с нагрузкой, но иногда возникают трудности в понимании нового материала. Если материал разобран, то остается в памяти и используется в будущем.',
        'Хорошо усваивает полученный материал, с легкостью находит необходимые механизмы программирования в уже написанный проектах.',
        'Справляется чаще самостоятельно, но не очень любит искать ошибки в своем коде.',
        'Понимает что за чем следует и выстраивает связи между тем что необходимо сделать и что он может сделать.',
        'Хорошо ориентируется в документации. Читает ее не спеша и с полным пониманием. Легко усваивает новый материал.',

    ],
    'water': [
        'очень самостоятельный ученик,',
        'целеустремленный ученик,',
        'общительный и разносторонний ученик,',
        'любознательный и ответственный ученик,',
        'достаточно способный ученик,',
        'достаточный самостоятельный и амбициозный ученик,',
        'коммуникативный и очень сообразительный ученик,'
    ],
    'difficulties': [
        'Трудности возникают редко, чаще сама решает их.',
        'Трудности возникают, но чаще справляется самостоятельно, пока учимся анализировать программу.',
        'Хорошо усваивает материал, есть некоторые трудности со внимательностью, но быстро исправляется.',
        'Допускает незначительные ошибки в написании кода.',
        'Трудности возникают только в понимании что именно необходимо сделать.',
        'Не очень любит искать ошибки с своем коде.'
    ],
    'behaviour': [
        'Спокойно, не отвлекаясь работает над проектами.',
        'Иногда задает интересные вопросы связанные с темой урока. Чаще вопросы для общего просветления.',
        'Любит максимально упростить выполнение заданий, что является огромным плюсом для программиста.',
        'Задает много вопросов, которые его интересуют.',
        'Просит помощи только если в этом есть необходимость.',

    ],
    'end': [
        'отлично справляется со всеми задачами.',
        'самостоятельно анализирует и выполняет задачи.',
        'полностью сконцентрирован на обучении.',
        'с нагрузкой справляется отлично, никакие замечаний нет.',
        'никаких замечаний или нареканий не получает.',
    ],
    'ulta': [
        '',
        'Как педагог могу твердо сказать, что общение и работа с данным учеником вызывает только положительные эмоции. ',
        '',
    ]

}


def save_feedback(file_path, feedbacks):
    writer = pandas.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay')
    wb = writer.book
    data_frame = pandas.DataFrame({'ОС': feedbacks})
    data_frame.to_excel(writer, sheet_name='feedback', index=False, startcol=6)
    wb.save(file_path)


def read_excel(file_path='feedback.xlsx'):
    return pandas.read_excel(
        file_path,
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


def generate_feedback(student, dont_use_link=False, manual_additions=False):
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
                return 'Не удалось получить информацию с сайта девман'
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
        water = random.choice(PHRASES['water'])
        behaviour = random.choice(PHRASES['behaviour'])
        end = random.choice(PHRASES['end'])
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
            {student["Имя для ОС"]} {water} {work_status} {lesson_number} проект курса {module_name} 
            в ходе которого {knowledge_status} {module_knowledge}. {behaviour} {commendation} На занятиях {end}
        ''')
        print(feedback)

        if manual_additions:
            additions = input('Чем дополним ОС?\n')
            feedback += additions
            print(feedback, '\n')

        return feedback.replace('\n', ' ')
    except KeyError:
        print(f'Модуля {module_name} нет в скрипте, ОС по {student["ФИО"]} не сгенерирована')
        return 'Текущего модуля нет в скрипте'


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
    students = read_excel('feedback.xlsx')

    feedbacks = []
    for student in students:
        feedback = generate_feedback(student, dont_use_link, manual_additions)
        feedbacks.append(feedback)

    if not dont_save:
        save_feedback('feedback.xlsx', feedbacks)


if __name__ == '__main__':
    main()
