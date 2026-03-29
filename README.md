# Task Manager - Gestor de Tareas Avanzado

Sistema de gestión de tareas tipo Trello desarrollado con Django.

**Demo en vivo:** https://rjardi.pythonanywhere.com

## Funcionalidades

- Registro, login y logout de usuarios
- CRUD de tableros y tareas
- Listas de tareas personalizables (columnas tipo Kanban)
- Drag & drop para mover tareas entre listas
- Asignación de tareas a usuarios
- Prioridades (Baja, Media, Alta)
- Etiquetas con colores personalizados
- Fechas límite
- Gestión de miembros del tablero
- Exportación a CSV y JSON
- Notificaciones por email

## Instalación

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Tecnologías

- Python 3.12
- Django 6
- Bootstrap 5
- Vanilla JavaScript (drag & drop)
- SQLite
