from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone

from .constants import PAGINATION_ELEMENTS_COUNT


def get_select_related(queryset):
    return queryset.select_related(
        'author',
        'location',
        'category',
    )


def filter_posts_by_publication(queryset):
    return queryset.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True,
    )


def annotate_and_sort_posts(queryset):
    return queryset.annotate(
        comment_count=Count('comments')
    )\
        .order_by('-pub_date')


def paginate(queryset, request, count=PAGINATION_ELEMENTS_COUNT):
    paginator = Paginator(queryset, count)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
