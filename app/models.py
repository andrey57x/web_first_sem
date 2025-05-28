from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db import models
from django.db.models import Sum, Value, Count
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.

class QuestionManager(models.Manager):
    def get_new(self):
        return super().all()

    def get_hot(self):
        return self.annotate(popularity=Coalesce(Sum('question_likes__value'), Value(0))).order_by('-popularity')


class AnswerManager(models.Manager):
    def get_new(self):
        return super().all()

    def get_hot(self):
        return self.annotate(popularity=Coalesce(Sum('answer_likes__value'), Value(0))).order_by('-is_correct','-popularity','-created_at')


# M-M with Question
class Tag(models.Model):

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

    search_vector = SearchVectorField(null=True, blank=True)

    @property
    def rating(self):
        r = self.question_likes.all().aggregate(rating=Sum('value'))['rating']
        return r if r else 0

    @property
    def answers_count(self):
        return self.answers.count()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            GinIndex(fields=['search_vector'], name='question_search_idx')
        ]

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

    class Meta:
        ordering = ['-created_at']

    @property
    def rating(self):
        r = self.answer_likes.all().aggregate(rating=Sum('value'))['rating']
        return r if r else 0


# 1-1 with User
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        default='avatars/default.jpg'
    )
    nickname = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# 1-M with Question, 1-1 with User
class QuestionLike(models.Model):
    RATING_CHOICES = [
        (1, 'Like'),
        (-1, 'Dislike'),
    ]
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question_likes', db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    value = models.IntegerField(choices=RATING_CHOICES, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('question', 'user')
        constraints = [
            models.CheckConstraint(check=models.Q(value__in=[1, -1]), name='question_like_value_check'),
        ]


# 1-M with Answer, 1-1 with User
class AnswerLike(models.Model):
    RATING_CHOICES = [
        (1, 'Like'),
        (-1, 'Dislike'),
    ]
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='answer_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    value = models.SmallIntegerField(choices=RATING_CHOICES, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('answer', 'user')
        constraints = [
            models.CheckConstraint(check=models.Q(value__in=[1, -1]), name='answer_like_value_check'),
        ]

@receiver(post_save, sender=Question)
def update_question_search_vector(sender, instance, **kwargs):
    # Обновление поискового вектора при сохранении
    Question.objects.filter(pk=instance.pk).update(
        search_vector=SearchVector('title', 'text')
    )