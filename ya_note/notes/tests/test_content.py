from notes.forms import NoteForm
from .conftest import TestFixtures


class TestContent(TestFixtures):

    def test_author_note_in_list(self):
        """Проверяем что зметка автора есть в списке у автора."""
        response = self.author_client.get(self.list_url)
        object_list = response.context['object_list']
        count_note = object_list.count()
        self.assertEqual(count_note, 1)
        self.assertEqual(self.note.title, object_list[0].title)
        self.assertEqual(self.note.text, object_list[0].text)
        self.assertEqual(self.note.slug, object_list[0].slug)
        self.assertEqual(self.note.author, object_list[0].author)

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
