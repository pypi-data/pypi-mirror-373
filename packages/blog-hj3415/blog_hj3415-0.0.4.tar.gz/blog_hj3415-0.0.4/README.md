# blog-hj3415

# settings.py
INSTALLED_APPS += ['blog_hj3415', 'markdownx']
AUTH_USER_MODEL = "blog_hj3415.User"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# urls.py
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += [path('markdownx/', include('markdownx.urls'))]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 템플릿에서
<div class="prose">{{ post.body_html|safe }}</div>