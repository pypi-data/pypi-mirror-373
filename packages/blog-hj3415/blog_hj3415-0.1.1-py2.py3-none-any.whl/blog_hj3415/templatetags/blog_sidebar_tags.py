# templatetags/blog_sidebar_tags.py
from django import template
from django.db.models import Count, Q
from blog_hj3415.models import BlogCategory, Post
from blog_hj3415.forms import SearchForm

register = template.Library()

@register.inclusion_tag('blog_hj3415/_sidebar_proxy.html', takes_context=True)
def sidebar(context, template_name, latest_limit=6):
    request = context.get('request')

    categories = (BlogCategory.objects
                  .annotate(post_count=Count('posts', filter=Q(posts__status='PUBLISHED')))
                  .order_by('name'))

    latest = (Post.published.all()
    .select_related('author', 'category')
    .order_by('-updated_at')[:latest_limit])

    return {
        'template_name': template_name,
        'form': SearchForm(request.GET or None),
        'categories': categories,
        'latest': latest,
        'request': request,  # include된 템플릿에서 csrf 등 사용
    }