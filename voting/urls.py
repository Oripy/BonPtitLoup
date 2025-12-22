from django.urls import path
from . import views

app_name = 'voting'

urlpatterns = [
    path('', views.date_group_list, name='list'),
    path('<int:group_id>/vote/', views.vote_view, name='vote'),
    path('<int:group_id>/results/', views.results_view, name='results'),
]

