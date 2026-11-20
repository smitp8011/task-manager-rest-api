from django.contrib import admin
from .models import Category, Task


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at']
    search_fields = ['name', 'user__username']
    list_filter = ['created_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'priority', 'status', 'due_date', 'created_at']
    list_filter = ['priority', 'status', 'due_date', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    list_editable = ['priority', 'status']
