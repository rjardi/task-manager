import csv
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q

from .models import Board, TaskList, Task, Label
from .forms import RegisterForm, BoardForm, TaskListForm, TaskForm, LabelForm


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('board_list')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def board_list(request):
    boards = Board.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct()
    return render(request, 'boards/board_list.html', {'boards': boards})


@login_required
def board_create(request):
    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.owner = request.user
            board.save()
            # Crear listas por defecto
            TaskList.objects.create(name='Por hacer', board=board, position=0)
            TaskList.objects.create(name='En progreso', board=board, position=1)
            TaskList.objects.create(name='Hecho', board=board, position=2)
            return redirect('board_detail', pk=board.pk)
    else:
        form = BoardForm()
    return render(request, 'boards/board_form.html', {'form': form, 'title': 'Crear Tablero'})


@login_required
def board_detail(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if board.owner != request.user and request.user not in board.members.all():
        return redirect('board_list')
    task_lists = board.task_lists.prefetch_related('tasks', 'tasks__labels', 'tasks__assigned_to')
    return render(request, 'boards/board_detail.html', {
        'board': board,
        'task_lists': task_lists,
    })


@login_required
def board_edit(request, pk):
    board = get_object_or_404(Board, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = BoardForm(request.POST, instance=board)
        if form.is_valid():
            form.save()
            return redirect('board_detail', pk=board.pk)
    else:
        form = BoardForm(instance=board)
    return render(request, 'boards/board_form.html', {'form': form, 'title': 'Editar Tablero'})


@login_required
def board_delete(request, pk):
    board = get_object_or_404(Board, pk=pk, owner=request.user)
    if request.method == 'POST':
        board.delete()
        return redirect('board_list')
    return render(request, 'boards/board_confirm_delete.html', {'board': board})


@login_required
def board_members(request, pk):
    board = get_object_or_404(Board, pk=pk, owner=request.user)
    from django.contrib.auth.models import User
    if request.method == 'POST':
        username = request.POST.get('username', '')
        try:
            user = User.objects.get(username=username)
            if user != board.owner:
                board.members.add(user)
        except User.DoesNotExist:
            pass
        return redirect('board_members', pk=board.pk)
    members = board.members.all()
    return render(request, 'boards/board_members.html', {'board': board, 'members': members})


@login_required
def remove_member(request, pk, user_id):
    board = get_object_or_404(Board, pk=pk, owner=request.user)
    from django.contrib.auth.models import User
    user = get_object_or_404(User, pk=user_id)
    board.members.remove(user)
    return redirect('board_members', pk=board.pk)


# TaskList views
@login_required
def tasklist_create(request, board_pk):
    board = get_object_or_404(Board, pk=board_pk)
    if board.owner != request.user and request.user not in board.members.all():
        return redirect('board_list')
    if request.method == 'POST':
        form = TaskListForm(request.POST)
        if form.is_valid():
            tl = form.save(commit=False)
            tl.board = board
            tl.position = board.task_lists.count()
            tl.save()
            return redirect('board_detail', pk=board.pk)
    else:
        form = TaskListForm()
    return render(request, 'boards/tasklist_form.html', {'form': form, 'board': board})


@login_required
def tasklist_delete(request, pk):
    tl = get_object_or_404(TaskList, pk=pk)
    board = tl.board
    if board.owner != request.user:
        return redirect('board_detail', pk=board.pk)
    if request.method == 'POST':
        tl.delete()
    return redirect('board_detail', pk=board.pk)


# Task views
@login_required
def task_create(request, tasklist_pk):
    task_list = get_object_or_404(TaskList, pk=tasklist_pk)
    board = task_list.board
    if board.owner != request.user and request.user not in board.members.all():
        return redirect('board_list')
    if request.method == 'POST':
        form = TaskForm(request.POST, board=board)
        if form.is_valid():
            task = form.save(commit=False)
            task.task_list = task_list
            task.position = task_list.tasks.count()
            task.save()
            form.save_m2m()
            return redirect('board_detail', pk=board.pk)
    else:
        form = TaskForm(board=board)
    return render(request, 'boards/task_form.html', {'form': form, 'board': board, 'title': 'Nueva Tarea'})


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    board = task.task_list.board
    if board.owner != request.user and request.user not in board.members.all():
        return redirect('board_list')
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, board=board)
        if form.is_valid():
            form.save()
            return redirect('board_detail', pk=board.pk)
    else:
        form = TaskForm(instance=task, board=board)
    return render(request, 'boards/task_form.html', {'form': form, 'board': board, 'title': 'Editar Tarea'})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    board = task.task_list.board
    if board.owner != request.user and request.user not in board.members.all():
        return redirect('board_list')
    if request.method == 'POST':
        task.delete()
    return redirect('board_detail', pk=board.pk)


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    board = task.task_list.board
    if board.owner != request.user and request.user not in board.members.all():
        return redirect('board_list')
    return render(request, 'boards/task_detail.html', {'task': task, 'board': board})


# API para mover tareas con drag and drop
@login_required
@require_POST
def move_task(request):
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        new_list_id = data.get('new_list_id')
        new_position = data.get('position', 0)

        task = Task.objects.get(pk=task_id)
        board = task.task_list.board

        if board.owner != request.user and request.user not in board.members.all():
            return JsonResponse({'error': 'No autorizado'}, status=403)

        new_list = TaskList.objects.get(pk=new_list_id, board=board)

        # Actualizar posiciones
        old_list = task.task_list
        task.task_list = new_list
        task.position = new_position
        task.save()

        # Reordenar tareas en ambas listas
        for i, t in enumerate(old_list.tasks.exclude(pk=task.pk).order_by('position')):
            t.position = i
            t.save()
        for i, t in enumerate(new_list.tasks.order_by('position')):
            if t.pk != task.pk:
                t.position = i + (1 if i >= new_position else 0)
                t.save()

        return JsonResponse({'status': 'ok'})
    except (Task.DoesNotExist, TaskList.DoesNotExist):
        return JsonResponse({'error': 'No encontrado'}, status=404)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'error': 'Datos inválidos'}, status=400)


# Labels
@login_required
def label_create(request, board_pk):
    board = get_object_or_404(Board, pk=board_pk, owner=request.user)
    if request.method == 'POST':
        form = LabelForm(request.POST)
        if form.is_valid():
            label = form.save(commit=False)
            label.board = board
            label.save()
            return redirect('board_detail', pk=board.pk)
    else:
        form = LabelForm()
    return render(request, 'boards/label_form.html', {'form': form, 'board': board})


@login_required
def label_delete(request, pk):
    label = get_object_or_404(Label, pk=pk)
    board = label.board
    if board.owner != request.user:
        return redirect('board_detail', pk=board.pk)
    if request.method == 'POST':
        label.delete()
    return redirect('board_detail', pk=board.pk)


# Exportar tareas
@login_required
def export_csv(request, board_pk):
    board = get_object_or_404(Board, pk=board_pk)
    if board.owner != request.user and request.user not in board.members.all():
        return redirect('board_list')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="tablero_{board.pk}_tareas.csv"'

    writer = csv.writer(response)
    writer.writerow(['Tarea', 'Lista', 'Prioridad', 'Asignado a', 'Fecha límite', 'Etiquetas'])

    for tl in board.task_lists.all():
        for task in tl.tasks.all():
            labels = ', '.join([l.name for l in task.labels.all()])
            writer.writerow([
                task.title,
                tl.name,
                task.get_priority_display(),
                task.assigned_to.username if task.assigned_to else '',
                task.due_date or '',
                labels,
            ])

    return response


@login_required
def export_json(request, board_pk):
    board = get_object_or_404(Board, pk=board_pk)
    if board.owner != request.user and request.user not in board.members.all():
        return redirect('board_list')

    data = {
        'board': board.name,
        'lists': []
    }

    for tl in board.task_lists.all():
        list_data = {
            'name': tl.name,
            'tasks': []
        }
        for task in tl.tasks.all():
            list_data['tasks'].append({
                'title': task.title,
                'description': task.description,
                'priority': task.priority,
                'assigned_to': task.assigned_to.username if task.assigned_to else None,
                'due_date': str(task.due_date) if task.due_date else None,
                'labels': [l.name for l in task.labels.all()],
            })
        data['lists'].append(list_data)

    response = HttpResponse(
        json.dumps(data, indent=2, ensure_ascii=False),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="tablero_{board.pk}_tareas.json"'
    return response


# Notificacion por email
@login_required
@require_POST
def notify_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.assigned_to and task.assigned_to.email:
        send_mail(
            subject=f'Tarea asignada: {task.title}',
            message=f'Se te ha asignado la tarea "{task.title}" en el tablero "{task.task_list.board.name}".\n\nDescripción: {task.description}\nPrioridad: {task.get_priority_display()}\nFecha límite: {task.due_date or "Sin fecha"}',
            from_email='noreply@taskmanager.com',
            recipient_list=[task.assigned_to.email],
        )
        return JsonResponse({'status': 'Email enviado'})
    return JsonResponse({'error': 'El usuario no tiene email'}, status=400)
