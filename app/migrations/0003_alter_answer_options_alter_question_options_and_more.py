# Generated by Django 5.2 on 2025-04-07 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_profile_avatar_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ['-created_at']},
        ),
        migrations.RemoveField(
            model_name='tag',
            name='color',
        ),
        migrations.AlterField(
            model_name='question',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='questions', to='app.tag'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
