from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from datetime import date, timedelta
from .models import Task
from collections import OrderedDict


class SigninTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test',
                                                         password='12test12',
                                                         email='test@example.com')
        self.user.save()

    def tearDown(self):
        self.user.delete()

    def test_correct(self):
        user = authenticate(username='test', password='12test12')
        self.assertTrue((user is not None) and user.is_authenticated)

    def test_wrong_username(self):
        user = authenticate(username='wrong', password='12test12')
        self.assertFalse(user is not None and user.is_authenticated)

    def test_wrong_pssword(self):
        user = authenticate(username='test', password='wrong')
        self.assertFalse(user is not None and user.is_authenticated)


class TaskTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test',
                                                         password='12test12',
                                                         email='test@example.com')
        self.user.save()
        self.timestamp = date.today()
        self.task = Task(user=self.user,
                         description='description',
                         due=self.timestamp + timedelta(days=1))
        self.task.save()

    def tearDown(self):
        self.user.delete()

    def test_read_task(self):
        self.assertEqual(self.task.user, self.user)
        self.assertEqual(self.task.description, 'description')
        self.assertEqual(self.task.due, self.timestamp + timedelta(days=1))

    def test_update_task_description(self):
        self.task.description = 'new description'
        self.task.save()
        self.assertEqual(self.task.description, 'new description')

    def test_update_task_due(self):
        self.task.due = self.timestamp + timedelta(days=2)
        self.task.save()
        self.assertEqual(self.task.due, self.timestamp + timedelta(days=2))


class SignInViewTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test',
                                                         password='12test12',
                                                         email='test@example.com')

    def tearDown(self):
        self.user.delete()

    def test_correct(self):
        response = self.client.post('/signin/', {'username': 'test', 'password': '12test12'})
        self.assertTrue(response.data['authenticated'])

    def test_wrong_username(self):
        response = self.client.post('/signin/', {'username': 'wrong', 'password': '12test12'})
        self.assertFalse(response.data['authenticated'])

    def test_wrong_pssword(self):
        response = self.client.post('/signin/', {'username': 'test', 'password': 'wrong'})
        self.assertFalse(response.data['authenticated'])


class AllTasksViewTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test',
                                                         password='12test12',
                                                         email='test@example.com')
        self.user.save()
        self.timestamp = date.today()
        self.client.login(username='test', password='12test12')

    def tearDown(self):
        self.user.delete()

    def test_no_tasks(self):
        response = self.client.get('/all/')
        self.assertEqual(response.data, {'tasks': []})

    def test_one_task(self):
        self.task1 = Task(user=self.user,
                          description='description 1',
                          due=self.timestamp + timedelta(days=1))
        self.task1.save()
        response = self.client.get('/all/')
        self.assertEqual(response.data, {'tasks': [OrderedDict([('id', 1),
                                                                ('description', 'description 1'),
                                                                ('due', str(self.timestamp + timedelta(days=1)))])]})

    def test_two_tasks(self):
        self.task1 = Task(user=self.user,
                          description='description 1',
                          due=self.timestamp + timedelta(days=1))
        self.task1.save()
        self.task2 = Task(user=self.user,
                          description='description 2',
                          due=self.timestamp + timedelta(days=2))
        self.task2.save()
        response = self.client.get('/all/')
        self.assertEqual(response.data, {'tasks': [OrderedDict([('id', 1),
                                                                ('description', 'description 1'),
                                                                ('due', str(self.timestamp + timedelta(days=1)))]),
                                                   OrderedDict([('id', 2),
                                                                ('description', 'description 2'),
                                                                ('due', str(self.timestamp + timedelta(days=2)))])]})
