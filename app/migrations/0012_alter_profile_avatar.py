# Generated by Django 5.2 on 2025-05-03 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_alter_profile_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, default='avatars/default.jpg', null=True, upload_to='avatars/'),
        ),
    ]
