from django.urls import path
from . import views

urlpatterns = [
    # Boards
    path('', views.board_list, name='board_list'),
    path('create/', views.board_create, name='board_create'),
    path('<int:pk>/', views.board_detail, name='board_detail'),
    path('<int:pk>/edit/', views.board_edit, name='board_edit'),
    path('<int:pk>/delete/', views.board_delete, name='board_delete'),
    path('<int:pk>/members/', views.board_members, name='board_members'),
    path('<int:pk>/members/<int:user_id>/remove/', views.remove_member, name='remove_member'),
    path('<int:board_pk>/labels/create/', views.label_create, name='label_create'),
    path('labels/<int:pk>/delete/', views.label_delete, name='label_delete'),

    # Export
    path('<int:board_pk>/export/csv/', views.export_csv, name='export_csv'),
    path('<int:board_pk>/export/json/', views.export_json, name='export_json'),

    # TaskLists
    path('<int:board_pk>/list/create/', views.tasklist_create, name='tasklist_create'),
    path('list/<int:pk>/delete/', views.tasklist_delete, name='tasklist_delete'),

    # Tasks
    path('list/<int:tasklist_pk>/task/create/', views.task_create, name='task_create'),
    path('task/<int:pk>/', views.task_detail, name='task_detail'),
    path('task/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('task/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('task/<int:pk>/notify/', views.notify_task, name='notify_task'),

    # API
    path('api/move-task/', views.move_task, name='move_task'),
]
