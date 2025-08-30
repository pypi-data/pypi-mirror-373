# templatetags/blog_pagination.py
from django import template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

register = template.Library()

def _make_page_bundle(page_range, n=5):
    l = list(page_range)
    return [l[i:i+n] for i in range(0, len(l), n)]

@register.simple_tag(takes_context=True)
def paginate_page(context, queryset, per_page=6, page_param='page'):
    """
    사용: {% paginate_page posts 6 as page_obj %}
    """
    request = context.get('request')
    page = 1
    if request is not None:
        page = request.GET.get(page_param, 1)

    paginator = Paginator(queryset, per_page)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, TypeError, ValueError):
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj

@register.simple_tag
def paginate_bundle(page_obj, bundle_size=5):
    """
    사용: {% paginate_bundle page_obj 5 as page_bundle %}
    """
    bundles = _make_page_bundle(page_obj.paginator.page_range, n=bundle_size)
    for b in bundles:
        if page_obj.number in b:
            return b
    return []

@register.simple_tag
def paginate_is(page_obj):
    """
    사용: {% paginate_is page_obj as is_paginated %}
    """
    return page_obj.paginator.num_pages > 1