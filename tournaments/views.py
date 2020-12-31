'''
View class for tournaments application
'''
import datetime
import random
import requests as rq
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Avg
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from rest_framework import mixins, generics
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAdminUser
from .models import Tournament, Question, TournamentPlayer
from .serializers import TournamentSerializer


NUMBER_OF_QUESTIONS = 10

class Index(TemplateView):
    '''
    Index template class, includes profile method and signup method
    '''
    template_name = "index.html"

    @login_required
    def player(request):
        '''
        Player function, after login, return user to players.html
        '''
        return render(request, 'players.html')

    def signup(request):
        '''
        Signup Method, validates user signup credentials and if there is validation error
        then it will return the user to the signup page with error messages. If validation passes
        then it will send the user to the profile page.
        '''
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                return redirect('/player')
        else:
            form = UserCreationForm()
        return render(request, 'registration/signup.html', {'form': form})

class TournamentView(TemplateView):
    '''
    Tournament Class view,
    process the created tournament and list them out according to their dates
    such as past, ongoing, upcoming tournaments.
    '''
    @login_required
    def list_all_tournament(request):
        '''
        List all the tournaments in the database
        '''
        tournaments = Tournament.objects.all()
        return render(request, 'tournaments_list.html', {'tournaments': tournaments})

    @login_required
    def list_tournament_question(request, tournament_id):
        '''
        List all the question of a tournament
        '''
        questions = Question.objects.all().filter(tournament_id=tournament_id)
        return render(request, 'questions_list.html', {'questions': questions})

    @login_required
    def list_tournament_highscore(request, tournament_id):
        '''
        List the score, participant and average sore for a tournament
        '''
        tour_play = TournamentPlayer.objects.filter(tournament_id=tournament_id).order_by('-score')
        total_taken = tour_play.count()
        average = tour_play.aggregate(Avg('score'))
        return render(request, 'highscore.html',
                      {'tour_play': tour_play, 'total_taken': total_taken, 'average':average})

    @login_required
    def list_ongoing_tournament(request):
        '''
        List all ongoing tournaments in the database
        '''
        tournaments_ongoing = True
        tournaments = Tournament.objects.filter(start_date__lte=datetime.date.today(),
                                                end_date__gte=datetime.date.today())
        return render(request, 'tournaments_list.html',
                      {'tournaments': tournaments, 'tournaments_ongoing':tournaments_ongoing})

    @login_required
    def list_upcoming_tournament(request):
        '''
        List all upcoming tournaments in the database
        '''
        tournaments = Tournament.objects.filter(start_date__gte=datetime.date.today())
        return render(request, 'tournaments_list.html', {'tournaments': tournaments})

    @login_required
    def list_past_tournament(request):
        '''
        List all past tournaments in the database
        '''
        tournaments_ongoing = False
        tournaments = Tournament.objects.filter(end_date__lte=datetime.date.today())
        return render(request, 'tournaments_list.html',
                      {'tournaments': tournaments, 'tournaments_ongoing':tournaments_ongoing})

class TournamentList(mixins.ListModelMixin,
                     generics.GenericAPIView):
    """
    List all tournaments, using mixin web api navigation
    """
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        '''
        mixins get method
        '''
        return self.list(request, *args, **kwargs)


class TournamentDetail(mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       generics.GenericAPIView):
    """
    Retrieve, update or delete a tournament instance.
    """
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        '''
        mixins get method
        '''
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        '''
        mixins put method
        '''
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        '''
        mixins delete method
        '''
        return self.destroy(request, *args, **kwargs)

class TournamentCreate(mixins.RetrieveModelMixin,
                       mixins.CreateModelMixin,
                       mixins.ListModelMixin,
                       generics.GenericAPIView):
    """
    Create a new tournament and adding questions to the tournament.
    """
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        '''
        mixins get method
        '''
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        '''
        creating a tournament and get the question using api and store it together in the database
        '''
        tournament = self.create(request, *args, **kwargs)
        difficulty = tournament.data['difficulty']
        category = tournament.data['category']
        api_string = f'https://opentdb.com/api.php?amount=10&category={category}&difficulty={difficulty}&type=multiple'
        questions_json = rq.get(api_string).json() #requesting api from the link
        self.create_questions(questions_json, tournament)
        return tournament

    def create_questions(self, questions_json, tournament):
        '''Creating the 10 questions'''
        random_order = [1, 2, 3, 0] #declare array to randomize the choices' order
        for ques in range(NUMBER_OF_QUESTIONS):
            question = questions_json['results'][ques]['question']
            correct_answer = questions_json['results'][ques]['correct_answer']
            choices = [None, None, None, None] #declaring empty array
            #randoming the random_order array and filling in the choices
            random.shuffle(random_order)
            choices[random_order[0]] = questions_json['results'][ques]['incorrect_answers'][0]
            choices[random_order[1]] = questions_json['results'][ques]['incorrect_answers'][1]
            choices[random_order[2]] = questions_json['results'][ques]['incorrect_answers'][2]
            choices[random_order[3]] = questions_json['results'][ques]['correct_answer']
            Question.objects.create(tournament=Tournament.objects.get(id=tournament.data['id']),
                                    question=question,
                                    correct_answer=correct_answer,
                                    choices1=choices[0],
                                    choices2=choices[1],
                                    choices3=choices[2],
                                    choices4=choices[3])

class QuestionQuiz(TemplateView):
    '''
    Class view for 10 question quiz
    '''
    @login_required
    def start_tournament(request, tournament_id):
        '''
        Starting the tournament, this method check if the user
        has taken the tournament or not, if not it will get the
        tournament id and user id and create a database entry
        '''
        if not TournamentPlayer.objects.filter(tournament_id=tournament_id,
                                               player_id=request.user.id).exists():
            TournamentPlayer.objects.create(tournament=Tournament.objects.get(id=tournament_id),
                                            player=request.user)
            questions = Question.objects.all().filter(tournament_id=tournament_id)
            return render(request, 'question.html',
                          {'questions': questions, 'tournament_id':tournament_id})
        else:
            taken = 'You have taken the tournament already'
            return render(request, 'players.html', {'taken':taken})

    @login_required
    def results(request, tournament_id):
        '''
        Processing the number of correct answer the user has given
        and give a result
        '''
        questions = Question.objects.all().filter(tournament_id=tournament_id)
        #getting the question id so that it can retrieve the value(user answers) from the form
        question_ids = [str(questions[id].id)for id in range(len(questions))]
        user_answers = [request.POST.get(question_ids[id]) for id in range(len(questions))]
        #getting the incorrect answer's question
        incorrect_match_question = [questions[i] for i in range(len(questions))
                                    if questions[i].correct_answer != user_answers[i]]
        user_incorrect_answer = [user_answers[i] for i in range(len(questions))
                                 if questions[i].correct_answer != user_answers[i]]
        #count the correct answer
        correct_count = len(questions)-len(incorrect_match_question)
        #save score
        tour_play = TournamentPlayer.objects.get(tournament_id=tournament_id,
                                                 player_id=request.user.id)
        tour_play.score = correct_count
        tour_play.complete_date = datetime.date.today()
        tour_play.save()
        return render(request, 'results.html',
                      {'user_incorrect_answer':user_incorrect_answer,
                       'correct_count':correct_count,
                       'incorrect_match_question':incorrect_match_question})
