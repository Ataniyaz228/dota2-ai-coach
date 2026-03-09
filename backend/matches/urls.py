from django.urls import path
from matches import views

urlpatterns = [
    path('dashboard/overview/<int:account_id>/', views.dashboard_overview, name='dashboard-overview'),
    path('dashboard/matches/<int:account_id>/', views.dashboard_matches, name='dashboard-matches'),
    path('dashboard/match/<int:match_id>/', views.dashboard_match_detail, name='dashboard-match-detail'),
    path('dashboard/heroes/<int:account_id>/', views.dashboard_heroes, name='dashboard-heroes'),
    path('dashboard/trends/<int:account_id>/', views.dashboard_trends, name='dashboard-trends'),
    path('heroes/', views.heroes_list, name='heroes-list'),
]
