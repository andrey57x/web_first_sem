from django.core.management.base import BaseCommand
from django.core.cache import cache
from app.popular import get_popular_tags, get_top_users


class Command(BaseCommand):
    help = 'Обновление кэша для популярных тегов и лучших пользователей'

    def handle(self, *args, **options):
        cache.set('popular_tags', get_popular_tags(), None)
        cache.set('top_users', get_top_users(), None)
        self.stdout.write('Кэш успешно обновлен')