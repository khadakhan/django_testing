from notes.forms import NoteForm
from .conftest import TestFixtures


class TestContent(TestFixtures):

    def test_author_note_in_list(self):
        """Проверяем что зметка автора есть в списке у автора."""
        response = self.author_client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertEqual(object_list.count(), 1)
        note_in_list = object_list[0]
        self.assertEqual(self.note.title, note_in_list.title)
        self.assertEqual(self.note.text, note_in_list.text)
        self.assertEqual(self.note.slug, note_in_list.slug)
        self.assertEqual(self.note.author, note_in_list.author)

    def test_not_author_note_in_list(self):
        """Проверяем что заметки автора нет в списке не автора."""
        response = self.not_author_client.get(self.list_url)
        object_list = response.context['object_list']
        count_note = object_list.count()
        self.assertEqual(count_note, 0)

    def test_pages_contains_form(self):
        """Проверяем, что на страницы заметки передаются формы."""
        urls_form = (self.add_url, self.edit_url)
        for url in urls_form:
            with self.subTest(name=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
