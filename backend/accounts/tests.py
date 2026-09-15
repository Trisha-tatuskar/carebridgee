from django.test import TestCase
from django.contrib.auth.models import User
from .models import SupportCenter

class BasicTest(TestCase):
    def test_create_support_center(self):
        u = User.objects.create_user(username='tuser', password='pass1234')
        center = SupportCenter.objects.create(
            user=u,
            name='TestCenter',
            center_type='NGO',
            address='Somewhere',
            phone='1234567890',
            email='ngo@example.com',
            latitude=12.34,
            longitude=56.78
        )
        self.assertEqual(center.name, 'TestCenter')
