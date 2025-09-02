# models.py
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify
from .managers import PublishedManager, PostQuerySet
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    photo = models.ImageField(upload_to="avatars/%Y/%m/%d", blank=True, null=True)
    nickname = models.CharField('nickname', default='default', max_length=40)
    sns = models.URLField('sns', blank=True, help_text="공란 가능")
    desc = models.TextField('desc', null=True, blank=True)


class BlogCategory(models.Model):
    name = models.CharField('블로그 카테고리', max_length=50, unique=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    STATUS = (('DRAFT', 'Draft'), ('PUBLISHED', 'Published'))

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, db_index=True, allow_unicode=True, blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='posts')
    category = models.ForeignKey(BlogCategory, related_name='posts', on_delete=models.PROTECT)
    body = MarkdownxField()
    remarkable = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS, default='DRAFT', db_index=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PostQuerySet.as_manager()
    published = PublishedManager()

    @property
    def body_html(self):
        return markdownify(self.body)

    class Meta:
        ordering = ['-published_at', '-id']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['title']),
        ]
        constraints = [
            # 공개 상태면 published_at은 반드시 존재
            models.CheckConstraint(
                name='post_published_requires_published_at',
                check=Q(status='DRAFT') | Q(published_at__isnull=False),
            ),
        ]

    def __str__(self):
        return self.title

    def _make_unique_slug(self):
        base = slugify(self.title, allow_unicode=False)[:200] or 'post'
        slug = base
        i = 2
        while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            tail = f'-{i}'
            slug = (base[: 220 - len(tail)]) + tail
            i += 1
        return slug

    def save(self, *args, **kwargs):
        # 슬러그 자동 생성
        if not self.slug:
            self.slug = self._make_unique_slug()

        # 공개 상태인데 published_at이 없으면 지금 시각으로
        if self.status == 'PUBLISHED' and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)