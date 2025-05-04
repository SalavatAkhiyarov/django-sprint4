from django.contrib import admin

from .models import Category, Comments, Location, Post


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'slug', 'created_at')
    search_fields = ('title', 'description', 'slug')
    list_filter = ('is_published',)


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_published',)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'category',
        'location',
        'pub_date',
        'is_published',
        'created_at')
    search_fields = ('title', 'text', 'author__username')
    list_filter = ('is_published', 'category', 'location', 'pub_date')


class CommentsAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'text', 'created_at')
    search_fields = ('text', 'author__username', 'post__title')
    list_filter = ('author', 'created_at')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comments, CommentsAdmin)
