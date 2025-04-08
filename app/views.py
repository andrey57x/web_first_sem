from django.shortcuts import render
from django.core.paginator import Paginator
from app.models import Question
from app.models import Answer
from app.models import Tag

PER_PAGE = 4

def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    try:
        page_num = int(request.GET.get('page', 1))
        page = paginator.page(page_num)
        if not page:
            raise ValueError
    except:
        page = paginator.page(1)
    return page


# Create your views here.


def index(request):
    questions = Question.objects.get_new()
    page = paginate(questions, request, PER_PAGE)
    return render(request, 'index.html', context={'questions': page.object_list, 'page': page, 'tags': Tag.objects.get_popular()})


def hot(request):
    questions = Question.objects.get_hot()
    page = paginate(questions, request, PER_PAGE)
    return render(request, 'hot.html', context={'questions': page.object_list, 'page': page, 'tags': Tag.objects.get_popular()})


def question(request, question_id):
    question = Question.objects.get(id=question_id)
    answers = Answer.objects.filter(question=question)
    page = paginate(answers, request, PER_PAGE-1)
    return render(request, 'question.html',
                  context={'question': question, 'answers': page.object_list, 'page': page,
                           'tags': Tag.objects.get_popular()})


def tag(request, tag_name):
    tag = Tag.objects.get(name=tag_name)
    questions = Question.objects.filter(tags=tag)
    page = paginate(questions, request, PER_PAGE)
    return render(request, 'tag.html', context={'tag': tag,
                                                'questions': page.object_list, 'page': page, 'tags': Tag.objects.get_popular()})


def login(request):
    return render(request, 'login.html', context={'tags': Tag.objects.get_popular()})


def signup(request):
    return render(request, 'signup.html', context={'tags': Tag.objects.get_popular()})


def ask(request):
    return render(request, 'ask.html', context={'tags': Tag.objects.get_popular()})


def settings(request):
    return render(request, 'settings.html', context={'tags': Tag.objects.get_popular()})
