from django.urls import path
from coach import views

urlpatterns = [
    path('analyze/<int:account_id>/', views.coach_analyze, name='coach-analyze'),
    path('match/<int:match_id>/', views.coach_match, name='coach-match'),
    path('chat/<int:account_id>/', views.coach_chat, name='coach-chat'),
]
