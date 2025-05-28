from django.db.models import Sum, Count, OuterRef, Subquery, IntegerField, F
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.functions import Coalesce
from .models import Tag, Question, Answer

HOT_NUMBER = 10


def get_popular_tags():
    three_months_ago = timezone.now() - timezone.timedelta(days=90)
    return (
        Tag.objects
        .filter(questions__created_at__gte=three_months_ago)
        .annotate(num_questions=Count('questions'))
        .order_by('-num_questions')[:HOT_NUMBER]
    )


def get_top_users():
    one_week_ago = timezone.now() - timezone.timedelta(days=7)

    question_subquery = (
        Question.objects
        .filter(author=OuterRef('pk'), created_at__gte=one_week_ago)
        .values('author')
        .annotate(sum_total=Sum('question_likes__value'))
        .values('sum_total')[:1]
    )

    answer_subquery = (
        Answer.objects
        .filter(author=OuterRef('pk'), created_at__gte=one_week_ago)
        .values('author')
        .annotate(sum_total=Sum('answer_likes__value'))
        .values('sum_total')[:1]
    )

    return (
        User.objects
        .annotate(
            q_likes=Coalesce(Subquery(question_subquery, output_field=IntegerField()), 0),
            a_likes=Coalesce(Subquery(answer_subquery, output_field=IntegerField()), 0),
            total_likes=F('q_likes') + F('a_likes')
        )
        .order_by('-total_likes')[:HOT_NUMBER]
    )