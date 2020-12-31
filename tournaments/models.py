'''
Python class that holds the models of the tournaments application
'''
from django.db import models
from django.contrib.auth.models import User

DIFFICULTY_CHOICE = [('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')]
CATEGORY_CHOICE = [('21', 'Sports'), ('22', 'Geography'), ('23', 'History'), ('25', 'Art')]

class Tournament(models.Model):
    '''
    tournament model
    '''
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=200, choices=CATEGORY_CHOICE)
    difficulty = models.CharField(max_length=50, choices=DIFFICULTY_CHOICE)
    start_date = models.DateField('start date')
    end_date = models.DateField('end date')

class Question(models.Model):
    '''
    question model
    '''
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    question = models.CharField(max_length=1000)
    correct_answer = models.CharField(max_length=500)
    choices1 = models.CharField(max_length=500)
    choices2 = models.CharField(max_length=500)
    choices3 = models.CharField(max_length=500)
    choices4 = models.CharField(max_length=500)

class TournamentPlayer(models.Model):
    '''
    tournament many to many relationship with player model
    '''
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    complete_date = models.DateField('complete_date', null=True)
