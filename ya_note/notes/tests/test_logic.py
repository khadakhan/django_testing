from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .conftest import TestFixtures


class TestLogic(TestFixtures):
    def test_anonymous_user_cant_create_note(self):
        """Проверяем пост запрос анонимного пользователя.
        Аноним должен добавлять заметку в БД.
        """
        notes_count_before = Note.objects.count()
        self.anonimous.post(self.add_url, data=self.form_data)
        self.assertEqual(Note.objects.count(), notes_count_before)

    def test_authorized_user_can_create_note(self):
        """Проверяем, что пост запрос авторизованного пользователя.
        Авторизованный пользователь должен добавлять замуетку в БД.
        """
        Note.objects.all().delete()
        response = self.author_client.post(self.add_url,
                                           data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_empty_slug(self):
        """Проверка автомтического формирования слага.
        Если при создании заметки не заполнен slug,
        то он формируется автоматически,
        с помощью функции pytils.translit.slugify.
        """
        Note.objects.all().delete()
        self.form_data.pop('slug')
        response = self.author_client.post(self.add_url,
                                           data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.slug, slugify(self.form_data['title']))

    def test_author_can_delete_note(self):
        """Проверяем, что автор заметки может её успешно удалять."""
        notes_count_before = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), notes_count_before - 1)

    def test_not_author_cant_delete_note(self):
        """Проверяем, что не автор заметки не может её успешно удалять."""
        notes_count_before = Note.objects.count()
        response = self.not_author_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count_before)

    def test_author_can_edit_note(self):
        """Проверяем, что автор заметки может её редактировать."""
        notes_count_before = Note.objects.count()
        self.assertEqual(notes_count_before, 1)
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.note.author)

    def test_not_author_cant_edit_note(self):
        """Проверяем, что не автор заметки не может её редактировать."""
        notes_count_before = Note.objects.count()
        self.assertEqual(notes_count_before, 1)
        response = self.not_author_client.post(self.edit_url,
                                               data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get()
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        notes_count_before = Note.objects.count()
        self.assertEqual(notes_count_before, 1)
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(self.add_url,
                                           data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), notes_count_before)
