from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.contrib import auth

from app.forms import LoginForm, SignupForm, AskForm, AnswerForm, ProfileEditForm
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


def get_answer_position(question, target_answer_id):
    answers = Answer.objects.get_new().filter(question=question)

    answer_ids = list(answers.values_list('id', flat=True))

    try:
        return answer_ids.index(target_answer_id)
    except ValueError:
        return None


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
    answers = Answer.objects.get_new().filter(question=question)
    page = paginate(answers, request, PER_PAGE - 1)

    form = AnswerForm()
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(question=question, user=request.user)
            return HttpResponseRedirect(reverse('question', args=[question.id])+'?page='+str(get_answer_position(question, answer.id) // (PER_PAGE - 1) + 1))

    return render(request, 'question.html',
                  context={'question': question, 'answers': page.object_list, 'page': page,
                           'tags': Tag.objects.get_popular(), 'form': form})


def tag(request, tag_name):
    tag = Tag.objects.get(name=tag_name)
    questions = Question.objects.filter(tags=tag)
    page = paginate(questions, request, PER_PAGE)
    return render(request, 'tag.html', context={'tag': tag,
                                                'questions': page.object_list, 'page': page, 'tags': Tag.objects.get_popular()})


def login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = {'username': form.cleaned_data['login'], 'password': form.cleaned_data['password']}
            user = auth.authenticate(request, **data)
            if user:
                auth.login(request, user)
                return HttpResponseRedirect(request.GET.get('continue', reverse('index')))
            else:
                form.add_error('__all__', f'Invalid login or password')
    return render(request, 'login.html', context={'tags': Tag.objects.get_popular(), 'form': form})


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(request.GET.get('continue', reverse('index')))


def signup(request):
    form = SignupForm()
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return HttpResponseRedirect(request.GET.get('continue', reverse('index')))
    return render(request, 'signup.html', context={'tags': Tag.objects.get_popular(), 'form': form})


@login_required(redirect_field_name='continue', login_url=reverse_lazy('login'))
def ask(request):
    form = AskForm()
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            question = form.save(user=request.user)
            return HttpResponseRedirect(reverse('question', args=[question.id]))
    return render(request, 'ask.html', context={'tags': Tag.objects.get_popular(), 'form': form})


@login_required(redirect_field_name='continue', login_url=reverse_lazy('login'))
def profile_edit(request):
    form = ProfileEditForm(user=request.user)
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save(request.user)
            return HttpResponseRedirect(request.GET.get('continue', reverse('profile.edit')))
    return render(request, 'profile_edit.html', context={'tags': Tag.objects.get_popular(), 'form': form})
