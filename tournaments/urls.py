'''
This is the python file for all the urls path in tournaments application
'''
from django.urls import path
from django.views.generic import TemplateView
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

app_name = 'tournament'
urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('player', views.Index.player, name='player'),
    path('signup', views.Index.signup, name='signup'),
    path('tournaments/<int:tournament_id>/results', views.QuestionQuiz.results, name='results'),
    path('tournaments/<int:tournament_id>/start',
         views.QuestionQuiz.start_tournament, name='start_tournament'),
    path('tournaments/<int:tournament_id>/highscore',
         views.TournamentView.list_tournament_highscore, name='highscore'),
    path('tournaments/',
         views.TournamentView.list_all_tournament, name='list_all_tournament'),
    path('tournaments/ongoing',
         views.TournamentView.list_ongoing_tournament, name='list_ongoing_tournament'),
    path('tournaments/upcoming',
         views.TournamentView.list_upcoming_tournament, name='list_upcoming_tournament'),
    path('tournaments/past',
         views.TournamentView.list_past_tournament, name='list_past_tournament'),
    path('tournaments/<int:tournament_id>/questions',
         views.TournamentView.list_tournament_question, name='tournament_question'),
    path('tournaments_api/', views.TournamentList.as_view()),
    path('tournaments_api/<int:pk>/', views.TournamentDetail.as_view(), name='edit_tournament'),
    path('tournaments_api/create/', views.TournamentCreate.as_view(), name='create_tournament'),
]
urlpatterns = format_suffix_patterns(urlpatterns)
urlpatterns += router.urls
