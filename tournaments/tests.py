'''Test class. This class will test the application view, models, api and end to end connection using selenium'''
import datetime
from django.test import LiveServerTestCase, TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from .models import Tournament, TournamentPlayer, Question

class ModelTestCase(TestCase):
    '''Test case for model'''
    def setUp(self):
        '''creating tournament'''
        self.tourny = Tournament.objects.create(name='TestTournament',
                                                category='21',
                                                difficulty='easy',
                                                start_date=datetime.date.today(),
                                                end_date=datetime.date.today())
        #creating Question
        Question.objects.create(tournament=self.tourny,
                                question='TestQuestion',
                                correct_answer='right',
                                choices1='right',
                                choices2='choice',
                                choices3='choice',
                                choices4='choice')
        #creating user
        self.user = User.objects.create_user(username='jacob',
                                             email='jacob@example.com',
                                             password='top_secret')

        #creating tournamentplayer instance
        TournamentPlayer.objects.create(tournament=self.tourny,
                                        player=self.user,
                                        score=10,
                                        complete_date=datetime.date.today())

    def test_tournament_creation(self):
        '''testing creation of tournament'''
        test_tour = Tournament.objects.get(name='TestTournament')
        self.assertTrue(isinstance(test_tour, Tournament))
        self.assertEqual('TestTournament', test_tour.name)

    def test_question_creation(self):
        '''testing creation of question'''
        test_ques = Question.objects.get(question='TestQuestion')
        self.assertTrue(isinstance(test_ques, Question))
        self.assertTrue(isinstance(test_ques.tournament, Tournament))
        self.assertEqual('TestQuestion', test_ques.question)

    def test_tournamentplayer_creation(self):
        ''' testing creation of question'''
        test_tourp = TournamentPlayer.objects.get(player=self.user)
        self.assertTrue(isinstance(test_tourp.tournament, Tournament))
        self.assertTrue(isinstance(test_tourp.player, User))

class TournamentAPITestCase(APITestCase):
    '''Test case for api'''
    def setUp(self):
        password = 'mypassword'
        self.data = {
            "id": 100,
            "name": "test Tournament",
            "category": "21",
            "difficulty": "easy",
            "start_date": "2020-06-02",
            "end_date": "2020-06-26"
        }
        my_admin = User.objects.create_superuser('myuser', 'myemail@test.com', password)
        self.client.login(username=my_admin.username, password=password)

    def test_create_tournament(self):
        '''create tournament using the api'''
        url = reverse('tournament:create_tournament')
        response = self.client.post(url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tournament.objects.count(), 1)
        self.assertEqual(Tournament.objects.get().name, 'test Tournament')
        self.assertEqual(Question.objects.count(), 10)

    def test_delete_tournament(self):
        '''delete tournament using the api'''
        url = reverse('tournament:create_tournament')
        response = self.client.post(url, self.data, format='json')
        url = reverse('tournament:edit_tournament', kwargs={'pk': Tournament.objects.get().pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Tournament.objects.count(), 0)

    def test_put_tournament(self):
        '''update tournament using the api'''
        url = reverse('tournament:create_tournament')
        response = self.client.post(url, self.data, format='json')
        url = reverse('tournament:edit_tournament', kwargs={'pk': Tournament.objects.get().pk})
        data_changed = {
            "id": 100,
            "name": "test Tournament changed",
            "category": "21",
            "difficulty": "easy",
            "start_date": "2020-06-02",
            "end_date": "2020-06-26"
        }
        response = self.client.put(url, data_changed, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Tournament.objects.get().name, "test Tournament changed")

    def test_get_tournament(self):
        '''retrieve tournament using the api'''
        url = reverse('tournament:create_tournament')
        response = self.client.post(url, self.data, format='json')
        url = reverse('tournament:edit_tournament', kwargs={'pk': Tournament.objects.get().pk})
        response = self.client.get(url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class ViewTestCase(TestCase):
    '''Test case for views'''
    def setUp(self):
        '''#creating tournament'''
        self.tourny = Tournament.objects.create(name='TestTournament',
                                                category='21',
                                                difficulty='easy',
                                                start_date=datetime.date.today(),
                                                end_date=datetime.date.today())
        Tournament.objects.create(name='TestTournamentPast',
                                  category='21',
                                  difficulty='easy',
                                  start_date=datetime.datetime(1990, 5, 17),
                                  end_date=datetime.datetime(1990, 5, 20))
        Tournament.objects.create(name='TestTournamentfuture',
                                  category='21',
                                  difficulty='easy',
                                  start_date=datetime.datetime(2100, 5, 17),
                                  end_date=datetime.datetime(2100, 5, 20))
        #creating Question
        Question.objects.create(tournament=self.tourny,
                                question='TestQuestion',
                                correct_answer='right',
                                choices1='right',
                                choices2='choice',
                                choices3='choice',
                                choices4='choice')
        #creating user
        self.user = User.objects.create_user(username='jacob',
                                             email='jacob@example.com',
                                             password='top_secret')
        self.password = 'mypassword'
        self.my_admin = User.objects.create_superuser('myuser', 'myemail@test.com', self.password)

        #creating tournamentplayer instance
        TournamentPlayer.objects.create(tournament=self.tourny,
                                        player=self.user,
                                        score=10,
                                        complete_date=datetime.date.today())

    def test_index_class_login(self):
        '''testing the responce for the profile page'''
        self.client.login(username=self.my_admin.username, password=self.password)
        url = reverse('tournament:player')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hi myuser')

    def test_index_signup_form_common_password(self):
        '''testing common password error'''
        response = self.client.post(reverse('tournament:signup'), data={
            'username': 'ben',
            'password1': 'password',
            'password2': 'password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This password is too common')

    def test_index_signup_form_success(self):
        '''testing successful signup with strong password'''
        response = self.client.post(reverse('tournament:signup'), data={
            'username': 'ben',
            'password1': 'P@ssw0rd123',
            'password2': 'P@ssw0rd123'
        })
        self.client.login(username='ben', password='P@ssw0rd123')
        #redirected successful 302 status
        self.assertEqual(response.status_code, 302)

    def test_tournament_view_list_all_tournament(self):
        '''test all tournaments view'''
        self.client.login(username=self.my_admin.username, password=self.password)
        url = reverse('tournament:list_all_tournament')
        response = self.client.get(url)
        self.assertContains(response, 'TestTournament')
        self.assertContains(response, 'Sports')#category 21 is Sports
        self.assertContains(response, 'Easy')

    def test_tournament_view_list_question(self):
        '''test questions list view'''
        self.client.login(username=self.my_admin.username, password=self.password)
        url = reverse('tournament:tournament_question',
                      kwargs={'tournament_id': Tournament.objects.get(name='TestTournament').pk})
        response = self.client.get(url)
        self.assertContains(response, 'TestQuestion')

    def test_tournament_view_ongoing(self):
        '''test list ongoing tournaments view'''
        self.client.login(username=self.my_admin.username, password=self.password)
        url = reverse('tournament:list_ongoing_tournament')
        response = self.client.get(url)
        date_today = datetime.date.today()
        self.assertContains(response, date_today.strftime("%B %#d, %Y"))

    def test_tournament_view_past(self):
        '''test list past tournaments view'''
        self.client.login(username=self.my_admin.username, password=self.password)
        url = reverse('tournament:list_past_tournament')
        response = self.client.get(url)
        date_past = datetime.datetime(1990, 5, 20)
        self.assertContains(response, date_past.strftime("%B %#d, %Y"))

    def test_tournament_view_future(self):
        '''test list future tournaments view'''
        self.client.login(username=self.my_admin.username, password=self.password)
        url = reverse('tournament:list_upcoming_tournament')
        response = self.client.get(url)
        date_future = datetime.datetime(2100, 5, 20)
        self.assertContains(response, date_future.strftime("%B %#d, %Y"))

    def test_question_start_quiz(self):
        '''test start tournament view'''
        self.client.login(username=self.my_admin.username, password=self.password)
        url = reverse('tournament:start_tournament',
                      kwargs={'tournament_id': Tournament.objects.get(name='TestTournament').id})
        response = self.client.get(url)
        self.assertContains(response, "TestQuestion")
        self.assertContains(response, "Submit")

    def test_question_finish_quiz(self):
        '''test finish tournaments view'''
        self.client.login(username=self.my_admin.username, password=self.password)
        TournamentPlayer.objects.create(tournament=self.tourny,
                                        player=self.my_admin,
                                        score=10,
                                        complete_date=datetime.date.today())
        url = reverse('tournament:results',
                      kwargs={'tournament_id': Tournament.objects.get(name='TestTournament').id})
        question_id = Question.objects.get().id
        response = self.client.post(url, data={
            question_id: 'right'
        })
        self.assertContains(response, "Final Score: ")
        self.assertContains(response, "Incorrect Questions")

class AccountTestCase(LiveServerTestCase):
    '''End to end testing using selenium'''

    def test_login(self):
        '''#test login page'''
        driver = webdriver.Chrome(r'C:\Users\ASUS\Desktop\oosd-mvt-iofh\tournament\tournaments\chromedriver')        
        driver.get('http://127.0.0.1:8000/accounts/login/')
        username = driver.find_element_by_id('id_username')
        password = driver.find_element_by_id('id_password')
        submit = driver.find_element_by_tag_name('button')
        username.send_keys('admin')
        password.send_keys('P@ssw0rd123')
        submit.send_keys(Keys.RETURN)
   
    def test_signup(self):
        '''test login page'''
        driver = webdriver.Chrome(r'C:\Users\ASUS\Desktop\oosd-mvt-iofh\tournament\tournaments\chromedriver')
        driver.get('http://127.0.0.1:8000/signup')
        username = driver.find_element_by_id('id_username')
        password = driver.find_element_by_id('id_password1')
        password2 = driver.find_element_by_id('id_password2')
        submit = driver.find_element_by_tag_name('button')
        username.send_keys('admintest')
        password.send_keys('P@ssw0rd123')
        password2.send_keys('P@ssw0rd123')
        submit.send_keys(Keys.RETURN)
        