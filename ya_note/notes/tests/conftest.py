from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestFixtures(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author note')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Not Author note')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.anonimous = Client()
        cls.note = Note.objects.create(title='Note1', text='Text note1',
                                       author=cls.author)
        cls.slug = cls.note.slug
        cls.home_url = reverse('notes:home')
        cls.login_url = reverse('users:login')
        cls.logout_url = reverse('users:logout')
        cls.signup_url = reverse('users:signup')
        cls.detail_url = reverse('notes:detail', args=(cls.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.slug,))
        cls.add_url = reverse('notes:add')
        cls.list_url = reverse('notes:list')
        cls.success_url = reverse('notes:success')
        cls.form_data = {'title': 'note_title',
                         'text': 'note_text',
                         'slug': 'note_slug'}

        cls.urls_for_tests = (
            (cls.home_url, HTTPStatus.OK, None, None),
            (cls.login_url, HTTPStatus.OK, None, None),
            (cls.logout_url, HTTPStatus.OK, None, None),
            (cls.signup_url, HTTPStatus.OK, None, None),
            (cls.detail_url, f'{cls.login_url}?next={cls.detail_url}',
             HTTPStatus.OK, HTTPStatus.NOT_FOUND),
            (cls.edit_url, f'{cls.login_url}?next={cls.edit_url}',
             HTTPStatus.OK, HTTPStatus.NOT_FOUND),
            (cls.delete_url, f'{cls.login_url}?next={cls.delete_url}',
             HTTPStatus.OK, HTTPStatus.NOT_FOUND),
            (cls.add_url, f'{cls.login_url}?next={cls.add_url}',
             None, None),
            (cls.list_url, f'{cls.login_url}?next={cls.list_url}',
             None, None),
            (cls.success_url, f'{cls.login_url}?next={cls.success_url}',
             None, None)
        )
