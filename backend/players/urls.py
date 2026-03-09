from django.urls import path
from players import views

urlpatterns = [
    path('profile/link', views.link_account, name='link-account'),
    path('profile/<int:account_id>/', views.get_player, name='get-player'),
    path('profile/<int:account_id>/sync', views.trigger_sync, name='trigger-sync'),
]
