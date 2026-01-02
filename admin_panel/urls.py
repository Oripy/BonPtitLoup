from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('parents/', views.parents_list, name='parents_list'),
    path('parents/<int:parent_id>/reset-password/', views.reset_parent_password, name='reset_parent_password'),
    path('parents/<int:parent_id>/toggle-admin/', views.toggle_admin_status, name='toggle_admin_status'),
    path('parents/<int:parent_id>/delete/', views.delete_parent_account, name='delete_parent_account'),
    path('children/', views.children_list, name='children_list'),
    path('create/', views.date_group_create, name='create'),
    path('<int:pk>/edit/', views.date_group_edit, name='edit'),
    path('<int:pk>/delete/', views.date_group_delete, name='delete'),
    path('<int:pk>/results/', views.results_view, name='results'),
    path('<int:pk>/export/excel/', views.export_excel, name='export_excel'),
]

