# managers.py
from django.db import models
from django.utils import timezone
from django.db.models import Q


class PublishedManager(models.Manager):
    def get_queryset(self):
        return (super().get_queryset()
                .filter(status='PUBLISHED', published_at__lte=timezone.now()))

# 이렇게 해두면 호스트 앱에서 Post.published.all()[:6], Post.objects.published().by_category(cat_id) 같은 식으로 깔끔하게 재사용 가능합니다.

class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status='PUBLISHED', published_at__lte=timezone.now())
    def by_category(self, category_id):
        return self.filter(category_id=category_id)
    def search(self, q):
        return self.filter(Q(title__icontains=q) | Q(body__icontains=q))