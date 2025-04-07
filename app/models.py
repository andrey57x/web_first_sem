from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class QuestionManager(models.Manager):
    def get_new(self):
        return self.all()

    def get_hot(self):
        return self.order_by('-rating')

class TagManager(models.Manager):
    def get_popular(self):
        return self.order_by('-popularity')

# M-M with Question
class Tag(models.Model):
    objects = TagManager()

    name = models.CharField(max_length=100, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def popularity(self):
        return Question.objects.filter(tags=self).count()


# M-M with Tag, 1-M with Answer, 1-M with User
class Question(models.Model):
    objects = QuestionManager()

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True, related_name='questions')

    title = models.CharField(max_length=50)
    text = models.TextField(max_length=1000)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def rating(self):
        return sum(QuestionLike.objects.filter(question=self).values_list('value', flat=True))

    class Meta:
        ordering = ['-created_at']


# 1-M with Question, 1-M with User
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    text = models.TextField(max_length=1000)
    is_correct = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def rating(self):
        return sum(AnswerLike.objects.filter(answer=self).values_list('value', flat=True))

    class Meta:
        ordering = ['-created_at']


# 1-1 with User
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='static/img/avatar', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# 1-M with Question, 1-1 with User
class QuestionLike(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    value = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('question', 'user')
        constraints = [
            models.CheckConstraint(check=models.Q(value__gte=-1) & models.Q(value__lte=1), name='question_value_check'),
        ]


# 1-M with Answer, 1-1 with User
class AnswerLike(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    value = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('answer', 'user')
        constraints = [
            models.CheckConstraint(check=models.Q(value__gte=-1) & models.Q(value__lte=1), name='answer_value_check'),
        ]
