from django import template
from django.core.cache import cache

register = template.Library()

@register.inclusion_tag('layouts/right_column.html')
def show_right_column():
    return {
        'popular_tags': cache.get('popular_tags', []),
        'top_users': cache.get('top_users', []),
    }