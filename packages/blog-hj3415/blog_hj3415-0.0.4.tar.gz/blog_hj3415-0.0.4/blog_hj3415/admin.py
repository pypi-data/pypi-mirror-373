# admin.py
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.db.models import Count
from markdownx.admin import MarkdownxModelAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from markdownx.models import MarkdownxField
from markdownx.widgets import MarkdownxWidget

from .models import BlogCategory, Post, User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Profile", {"fields": ("nickname", "desc", "photo", "sns")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {"fields": ("nickname", "desc", "photo", "sns")}),
    )
    list_display = ("username", "nickname", "is_staff", "sns")

# ---------- 공통 액션 ----------
@admin.action(description="선택 글: 공개(PUBLISHED)로 전환")
def make_published(modeladmin, request, queryset):
    updated = queryset.update(status='PUBLISHED', published_at=timezone.now())
    modeladmin.message_user(request, f"{updated}개 글을 공개로 전환했습니다.")

@admin.action(description="선택 글: 초안(DRAFT)으로 전환")
def make_draft(modeladmin, request, queryset):
    updated = queryset.update(status='DRAFT', published_at=None)
    modeladmin.message_user(request, f"{updated}개 글을 초안으로 전환했습니다.")


# ---------- 카테고리 ----------
@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "posts_count")
    search_fields = ("name",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # 목록에서 카운트 쿼리 N+1 방지
        return qs.annotate(_posts_count=Count("posts"))

    @admin.display(ordering="_posts_count", description="게시글 수")
    def posts_count(self, obj):
        return obj._posts_count


# ---------- 게시글(Post) ----------
@admin.register(Post)
class PostAdmin(MarkdownxModelAdmin):  # Markdownx 편집 위젯/미리보기 적용
    list_display = (
        "title",
        "status_badge",
        "published_at",
        "category",
        "author",
        "thumbnail_tag",
        "updated_at",
    )
    list_filter = (
        "status",
        "category",
        ("published_at", admin.DateFieldListFilter),
    )
    search_fields = ("title", "body")
    date_hierarchy = "published_at"
    ordering = ("-published_at", "-id")
    actions = [make_published, make_draft]

    # 외래키 선택 UX (User, Category 검색 가능)
    autocomplete_fields = ("author", "category")

    # 작성/수정 시에 보일 필드 구성
    fieldsets = (
        (None, {
            "fields": ("title", "status", "remarkable", "category", "author")
        }),
        ("콘텐츠", {
            "fields": ("body", "thumbnail")
        }),
        ("메타", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    readonly_fields = ("created_at", "updated_at")  # 자동 필드 보호

    formfield_overrides = {
        MarkdownxField: {"widget": MarkdownxWidget},
    }

    # 목록 최적화
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("author", "category")

    # 상태 배지 출력(보기 편하게)
    @admin.display(description="상태", ordering="status")
    def status_badge(self, obj):
        color = "#16a34a" if obj.status == "PUBLISHED" else "#6b7280"
        label = "공개" if obj.status == "PUBLISHED" else "초안"
        return format_html(
            '<span style="display:inline-block;padding:2px 8px;border-radius:9999px;'
            f'background:{color};color:white;font-size:11px;">{label}</span>'
        )

    # 썸네일 미리보기
    @admin.display(description="썸네일")
    def thumbnail_tag(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="height:40px;border-radius:6px;" />', obj.thumbnail.url)
        return "-"

    class Media:
        css = {
            'all': ('admin/css/markdown_fix.css',)  # 위에서 만든 파일 경로
        }
    # 슬러그는 모델 save()에서 자동 생성하므로, 관리자에서 비워두면 자동 생성됨
    # 한국어 슬러그를 prepopulated_fields로 만들면 JS가 ASCII만 처리하는 이슈가 있으니 비권장
    # prepopulated_fields = {"slug": ("title",)}  # (영문 위주 사이트면 선택 사용)

    # "사이트에서 보기" 버튼을 쓰고 싶다면 모델에 get_absolute_url 구현 필요
    # def view_on_site(self, obj):
    #     return obj.get_absolute_url()


