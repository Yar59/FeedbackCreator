import requests
from bs4 import BeautifulSoup
from modules_knowledge import MODULES_KNOWLEDGE

def get_student_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return response


def get_lesson(page_content):
    soup = BeautifulSoup(page_content.text, 'lxml')
    latest_lesson = soup.select_one('div.card')
    module = latest_lesson.select_one('a.text-reset').text.replace('\n', '').strip()
    try:
        lesson = latest_lesson.select_one('div.lesson-container').text.split('/')[0].replace('\n', '').strip().split(' ')[1]
    except IndexError:
        lesson = len(MODULES_KNOWLEDGE.get(module))
    in_work = latest_lesson.select_one('div.steps')
    if in_work:
        status = 'В работе'
    else:
        status = 'Сдается'
    return {
        'module_name': module,
        'lesson_number': lesson,
        'lesson_status': status,
    }


def main():
    link = input('ссылка на ученика')
    page_content = get_student_page(link)
    print(get_lesson(page_content))


if __name__ == '__main__':
    main()
