from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Board, TaskList, Task, Label


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TaskListForm(forms.ModelForm):
    class Meta:
        model = TaskList
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la lista'}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'priority', 'labels', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'labels': forms.CheckboxSelectMultiple(),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, board=None, **kwargs):
        super().__init__(*args, **kwargs)
        if board:
            self.fields['assigned_to'].queryset = User.objects.filter(
                models.Q(id=board.owner.id) | models.Q(id__in=board.members.all())
            ).distinct()
            self.fields['labels'].queryset = Label.objects.filter(board=board)


class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }
