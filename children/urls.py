from django.urls import path
from . import views

app_name = 'children'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create/', views.child_create, name='create'),
    path('<int:pk>/edit/', views.child_edit, name='edit'),
    path('<int:pk>/delete/', views.child_delete, name='delete'),
]

