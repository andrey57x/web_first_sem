from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import auth
from django.views.decorators.http import require_POST

from app.forms import LoginForm, SignupForm, AskForm, AnswerForm, ProfileEditForm
from app.models import Question, QuestionLike, AnswerLike
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
    answers = Answer.objects.get_hot().filter(question=question)

    answer_ids = list(answers.values_list('id', flat=True))

    try:
        return answer_ids.index(target_answer_id)
    except ValueError:
        return None

def get_question_like(question, user):
    current_like = 0
    if user.is_authenticated:
        try:
            current_like = QuestionLike.objects.get(
                question=question,
                user=user
            ).value
        except QuestionLike.DoesNotExist:
            pass
    return current_like

def get_answer_like(answer, user):
    current_like = 0
    if user.is_authenticated:
        try:
            current_like = AnswerLike.objects.get(
                answer=answer,
                user=user
            ).value
        except AnswerLike.DoesNotExist:
            pass
    return current_like



# Create your views here.


def index(request):
    questions = Question.objects.get_new()
    page = paginate(questions, request, PER_PAGE)
    for question in page.object_list:
        question.current_like = get_question_like(question, request.user)
    return render(request, 'index.html', context={'questions': page.object_list, 'page': page, 'tags': Tag.objects.get_popular()})


def hot(request):
    questions = Question.objects.get_hot()
    page = paginate(questions, request, PER_PAGE)
    for question in page.object_list:
        question.current_like = get_question_like(question, request.user)
    return render(request, 'hot.html', context={'questions': page.object_list, 'page': page, 'tags': Tag.objects.get_popular()})


def question(request, question_id):
    question = Question.objects.get(id=question_id)
    answers = Answer.objects.get_hot().filter(question=question)
    page = paginate(answers, request, PER_PAGE - 1)

    form = AnswerForm()
    if request.method == 'POST' and request.user != question.author:
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(question=question, user=request.user)
            return HttpResponseRedirect(reverse('question', args=[question.id])+'?page='+str(get_answer_position(question, answer.id) // (PER_PAGE - 1) + 1))
    question.current_like = get_question_like(question, request.user)

    for answer in page.object_list:
        answer.current_like = get_answer_like(answer, request.user)

    return render(request, 'question.html',
                  context={'question': question, 'answers': page.object_list, 'page': page,
                           'tags': Tag.objects.get_popular(), 'form': form})


def tag(request, tag_name):
    tag = Tag.objects.get(name=tag_name)
    questions = Question.objects.filter(tags=tag)
    page = paginate(questions, request, PER_PAGE)
    for question in page.object_list:
        question.current_like = get_question_like(question, request.user)
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

@require_POST
@login_required(redirect_field_name='continue', login_url=reverse_lazy('login'))
def question_like(request, question_id):
    question = Question.objects.get(id=question_id)
    user = request.user
    value = int(request.GET.get('value'))
    state = 0
    if user != question.author:
        try:
            like = QuestionLike.objects.get(question=question, user=user)
            if like.value == value:
                like.delete()
            else:
                like.value = value
                like.save()
                state = like.value
        except QuestionLike.DoesNotExist:
            like = QuestionLike(question=question, user=user, value=value)
            like.save()
            state = like.value
    return JsonResponse({'rating': question.rating, 'state': state})

@require_POST
@login_required(redirect_field_name='continue', login_url=reverse_lazy('login'))
def answer_like(request, answer_id):
    answer = Answer.objects.get(id=answer_id)
    user = request.user
    value = int(request.GET.get('value'))
    state = 0
    if user != answer.author:
        try:
            like = AnswerLike.objects.get(answer=answer, user=user)
            if like.value == value:
                like.delete()
            else:
                like.value = value
                like.save()
                state = like.value
        except AnswerLike.DoesNotExist:
            like = AnswerLike(answer=answer, user=user, value=value)
            like.save()
            state = like.value
    return JsonResponse({'rating': answer.rating, 'state': state})

@require_POST
@login_required(redirect_field_name='continue', login_url=reverse_lazy('login'))
def answer_correct(request, answer_id):
    answer = Answer.objects.get(id=answer_id)
    user = request.user
    if user == answer.question.author:
        answer.is_correct = not answer.is_correct
        answer.save()
    return JsonResponse({'state': answer.is_correct})

