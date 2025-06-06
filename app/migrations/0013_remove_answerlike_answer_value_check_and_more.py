# Generated by Django 5.2 on 2025-05-15 14:21

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_alter_profile_avatar'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='answerlike',
            name='answer_value_check',
        ),
        migrations.RemoveConstraint(
            model_name='questionlike',
            name='question_value_check',
        ),
        migrations.AlterField(
            model_name='answerlike',
            name='value',
            field=models.SmallIntegerField(choices=[(1, 'Like'), (-1, 'Dislike')], db_index=True),
        ),
        migrations.AlterField(
            model_name='questionlike',
            name='value',
            field=models.IntegerField(choices=[(1, 'Like'), (-1, 'Dislike')], db_index=True),
        ),
        migrations.AddConstraint(
            model_name='answerlike',
            constraint=models.CheckConstraint(condition=models.Q(('value__in', [1, -1])), name='answer_like_value_check'),
        ),
        migrations.AddConstraint(
            model_name='questionlike',
            constraint=models.CheckConstraint(condition=models.Q(('value__in', [1, -1])), name='question_like_value_check'),
        ),
    ]
