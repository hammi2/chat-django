from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from http import HTTPStatus
from chat.models import Message,UserProfile

# Create your tests here.

class MessageTest(TestCase):

    def test_message(self):

        m = UserProfile.objects.count()
        print(m)
        self.assertEqual(m, 0)

    def test_homepage(self):
        response = self.client.get("/login/")

        self.assertTemplateUsed(response,'login.html')
        self.assertEqual(response.status_code,HTTPStatus.OK)
