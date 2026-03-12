from django.contrib import admin
from .models import Board, TaskList, Task, Label


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'created_at']
    list_filter = ['owner']


@admin.register(TaskList)
class TaskListAdmin(admin.ModelAdmin):
    list_display = ['name', 'board', 'position']
    list_filter = ['board']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'task_list', 'priority', 'assigned_to', 'due_date']
    list_filter = ['priority', 'task_list__board']
    search_fields = ['title']


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'board']
