from django.contrib import admin
from django.urls import path, include
from boards import views as board_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('boards.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', board_views.register, name='register'),
]
