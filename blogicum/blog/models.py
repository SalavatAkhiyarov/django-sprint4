from django.db import models
from django.contrib.auth import get_user_model

from .constants import MAX_LENGTH_CHAR_FIELD, STR_TITLE_LIMIT

User = get_user_model()


class CreatedAtAndIsPublishedAbstract(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Добавлено"
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликовано",
        help_text="Снимите галочку, чтобы скрыть публикацию."
    )

    class Meta:
        abstract = True


class Category(CreatedAtAndIsPublishedAbstract):
    title = models.CharField(
        max_length=MAX_LENGTH_CHAR_FIELD,
        verbose_name="Заголовок"
    )
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(
        unique=True,
        verbose_name="Идентификатор",
        help_text=(
            "Идентификатор страницы для URL; разрешены символы латиницы, "
            "цифры, дефис и подчёркивание."
        )
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title[:STR_TITLE_LIMIT]


class Location(CreatedAtAndIsPublishedAbstract):
    name = models.CharField(
        max_length=MAX_LENGTH_CHAR_FIELD,
        verbose_name="Название места"
    )

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name[:STR_TITLE_LIMIT]


class Post(CreatedAtAndIsPublishedAbstract):
    title = models.CharField(
        max_length=MAX_LENGTH_CHAR_FIELD,
        verbose_name="Заголовок"
    )
    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField(
        verbose_name="Дата и время публикации",
        help_text=(
            "Если установить дату и время в будущем — можно делать отложенные "
            "публикации."
        )
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        verbose_name="Местоположение",
        null=True,
        blank=True,
        related_name="posts"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория",
        related_name="posts"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор публикации",
        related_name="posts"
    )
    image = models.ImageField(verbose_name='Изображение', blank=True)

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'title',
                    'text',
                    'category',
                    'location',
                    'pub_date'),
                name='Unique post'),
        )

    def __str__(self):
        return self.title[:STR_TITLE_LIMIT]


class Comments(models.Model):
    text = models.TextField(verbose_name="Комментарий")
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Добавлено"
    )
