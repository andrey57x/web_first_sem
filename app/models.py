from django.db import models
from django.db.models import Sum, Value, Count
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User

HOT_TAGS_NUMBER = 8


# Create your models here.

class QuestionManager(models.Manager):
    def get_new(self):
        return super().all()

    def get_hot(self):
        return self.annotate(popularity=Coalesce(Sum('question_likes__value'), Value(0))).order_by('-popularity')


class TagManager(models.Manager):
    def get_popular(self):
        return self.annotate(popularity=Coalesce(Count('questions'), Value(0))).order_by('-popularity')[:HOT_TAGS_NUMBER]


class AnswerManager(models.Manager):
    def get_new(self):
        return super().all()

    def get_hot(self):
        return self.annotate(popularity=Coalesce(Sum('answer_likes__value'), Value(0))).order_by('-popularity')


# M-M with Question
class Tag(models.Model):
    objects = TagManager()

    name = models.CharField(max_length=100, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def color(self):
        colors = ["primary", "secondary", "success", "danger", "warning", "info", "light", "dark"]
        return colors[abs(hash(self.name)) % len(colors)]


# M-M with Tag, 1-M with Answer, 1-M with User
class Question(models.Model):
    objects = QuestionManager()

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True, related_name='questions')

    title = models.CharField(max_length=50, unique=True)
    text = models.TextField(max_length=1000)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def rating(self):
        r = self.question_likes.all().aggregate(rating=Sum('value'))['rating']
        return r if r else 0

    @property
    def answers_count(self):
        return self.answers.count()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# 1-M with Question, 1-M with User
class Answer(models.Model):
    objects = AnswerManager()

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    text = models.TextField(max_length=1000)
    is_correct = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def rating(self):
        r = self.answer_likes.all().aggregate(rating=Sum('value'))['rating']
        return r if r else 0


# 1-1 with User
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.CharField(max_length=100, blank=True, null=True)
    nickname = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# 1-M with Question, 1-1 with User
class QuestionLike(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question_likes', db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    value = models.IntegerField(default=0, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('question', 'user')
        constraints = [
            models.CheckConstraint(check=models.Q(value__gte=-1) & models.Q(value__lte=1), name='question_value_check'),
        ]


# 1-M with Answer, 1-1 with User
class AnswerLike(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='answer_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    value = models.IntegerField(default=0, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('answer', 'user')
        constraints = [
            models.CheckConstraint(check=models.Q(value__gte=-1) & models.Q(value__lte=1), name='answer_value_check'),
        ]
