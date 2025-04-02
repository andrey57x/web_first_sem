from django.shortcuts import render
from django.core.paginator import Paginator

QUESTIONS = [
    {
        "title": f"Title {i}",
        "id": i,
        "text": f"This is text for question # {i}",
        'img_path': 'img/kitten.jpg'
    } for i in range(30)
]

ANSWERS = [
    {
        "title": f"Answer title {i}",
        "id": i,
        "text": f"This is text for answer # {i}",
        'img_path': 'img/puppy.jpg'
    } for i in range(30)
]

POPULAR_TAGS = [{
    'name': 'python',
    'color': 'primary'
}, {
    'name': 'django',
    'color': 'secondary'
}, {
    'name': 'TechnoPark',
    'color': 'success'
}, {
    'name': 'Voloshin',
    'color': 'danger'
}, {
    'name': 'black-jack',
    'color': 'warning'
}, {
    'name': 'bender',
    'color': 'info'
}, {
    'name': 'Mail.Ru',
    'color': 'light'
}, {
    'name': 'Firefox',
    'color': 'dark'
}]


def paginate(objects_list, request, per_page=10):
    page_num = int(request.GET.get('page', 1))
    paginator = Paginator(objects_list, per_page)
    try:
        page = paginator.page(page_num)
        if not page:
            raise ValueError
    except:
        page = paginator.page(1)
    return page


# Create your views here.


def index(request):
    page = paginate(QUESTIONS, request, 4)
    return render(request, 'index.html', context={'questions': page.object_list, 'page': page, 'tags': POPULAR_TAGS})


def hot(request):
    q = QUESTIONS.copy()
    q.reverse()
    page = paginate(q, request, 4)
    return render(request, 'hot.html', context={'questions': page.object_list, 'page': page, 'tags': POPULAR_TAGS})


def question(request, question_id):
    page = paginate(ANSWERS, request, 3)
    return render(request, 'question.html', context={'question': QUESTIONS[question_id], 'answers': page.object_list, 'page': page, 'tags': POPULAR_TAGS})


def tag(request, tag_name):
    page = paginate(QUESTIONS, request, 4)
    return render(request, 'tag.html', context={'tag': [tag for tag in POPULAR_TAGS if tag['name'] == tag_name][0], 'questions': page.object_list, 'page': page, 'tags': POPULAR_TAGS})


def login(request):
    return render(request, 'login.html', context={'tags': POPULAR_TAGS})


def signup(request):
    return render(request, 'signup.html', context={'tags': POPULAR_TAGS})


def ask(request):
    return render(request, 'ask.html', context={'tags': POPULAR_TAGS})


def settings(request):
    return render(request, 'settings.html', context={'tags': POPULAR_TAGS})
