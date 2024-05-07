from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(title='note1',
                                       text='note1',
                                       slug='note1',
                                       author=cls.author)

    def test_notes_list_for_different_users(self):
        """Проверяем, что отдельная заметка передаётся на страницу со списком
        заметок в списке object_list, в словаре context;
        В список заметок одного пользователя не попадают заметки другого
        пользователя.
        """
        users_note_in_list = (
            (self.author, True),
            (self.reader, False),
        )
        for user, note_in_list in users_note_in_list:
            self.client.force_login(user)
            url = reverse('notes:list')
            response = self.client.get(url)
            object_list = response.context['object_list']
            assert (self.note in object_list) is note_in_list

    def test_pages_contains_form(self):
        """Проверяем, что на страницы создания и редактирования заметки
        передаются формы.
        """
        name_args = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        self.client.force_login(self.author)
        for name, args in name_args:
            url = reverse(name, args=args)
            response = self.client.get(url)
            assert 'form' in response.context
            assert isinstance(response.context['form'], NoteForm)
