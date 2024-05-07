from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNotePost(TestCase):
    ADD_URL = reverse('notes:add')
    SUCCESS_URL = reverse('notes:success')
    NOTE_TITLE = 'Титул'
    NOTE_TEXT = 'Текст'
    NOTE_SLUG = 'slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {'title': cls.NOTE_TITLE,
                         'text': cls.NOTE_TEXT,
                         'slug': cls.NOTE_SLUG}

    def test_anonymous_user_cant_create_note(self):
        """Проверяем, что пост запрос анонимного пользователя
        не добавил заметку в БД.
        """
        self.client.post(self.ADD_URL, data=self.form_data)
        self.assertEqual(Note.objects.count(), 0)

    def test_authorized_user_can_create_note(self):
        """Проверяем, что пост запрос авторизованного пользователя
        добавил заметку в БД
        """
        response = self.auth_client.post(self.ADD_URL,
                                         data=self.form_data)
        # Проверяем перенаправление на страницу успешного добавления.
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        # Проверяем итоговое совпадение атрибутов
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.author)

    def test_empty_slug(self):
        """Если при создании заметки не заполнен slug,
        то он формируется автоматически,
        с помощью функции pytils.translit.slugify.
        """
        self.form_data.pop('slug')
        response = self.auth_client.post(self.ADD_URL,
                                         data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        assert Note.objects.count() == 1
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        assert new_note.slug == expected_slug


class TestNoteEditDeleteDetail(TestCase):
    NOTE_TITLE = 'note1'
    NOTE_TEXT = 'note1'
    NOTE_SLUG = 'note1'
    NEW_NOTE_TITLE = 'note2'
    NEW_NOTE_TEXT = 'note2'
    NEW_NOTE_SLUG = 'note2'
    SUCCESS_URL = reverse('notes:success')
    ADD_URL = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        # Создадим автора заметки
        cls.author = User.objects.create(username='Лев Толстой')
        # Просто читатель
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(title=cls.NOTE_TITLE,
                                       text=cls.NOTE_TEXT,
                                       slug=cls.NOTE_SLUG,
                                       author=cls.author)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {'title': cls.NEW_NOTE_TITLE,
                         'text': cls.NEW_NOTE_TEXT,
                         'slug': cls.NEW_NOTE_SLUG}
        # авторизуем пользователей
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

    def test_author_can_delete_note(self):
        """Проверяем, что автор заметки может её успешно удалять."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 0)

    def test_not_author_cant_delete_note(self):
        """Проверяем, что не автор заметки не может её успешно удалять."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_note(self):
        """Проверяем, что автор заметки может её редактировать"""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NEW_NOTE_SLUG)
        self.assertEqual(self.note.author, self.author)

    def test_not_author_cant_edit_note(self):
        """Проверяем, что не автор заметки не может её редактировать"""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)
        self.assertEqual(self.note.author, self.author)

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(self.ADD_URL,
                                           data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        assert Note.objects.count() == 1
