from .conftest import TestFixtures


class TestRoutes(TestFixtures):

    def test_routes_anonimous(self):
        """Проеряем доступности страниц для анонимного пользователя."""
        for (url,
             anonimous_test,
             author_test,
             not_author_test) in self.urls_for_tests:
            with self.subTest(name=url):
                if not isinstance(anonimous_test, str):
                    response = self.anonimous.get(url)
                    self.assertEqual(response.status_code, anonimous_test)
                else:
                    response = self.anonimous.get(url)
                    self.assertRedirects(response, anonimous_test)

    def test_routes_author_client(self):
        """Проверяем доступность страниц для автора заметки."""
        for (url,
             anonimous_test,
             author_test,
             not_author_test) in self.urls_for_tests:
            with self.subTest(name=url):
                if author_test is not None:
                    response = self.author_client.get(url)
                    self.assertEqual(response.status_code, author_test)

    def test_routes_not_author_client(self):
        """Проверяем доступность страниц для не автора заметки."""
        for (url,
             anonimous_test,
             author_test,
             not_author_test) in self.urls_for_tests:
            with self.subTest(name=url):
                if not_author_test is not None:
                    response = self.not_author_client.get(url)
                    self.assertEqual(response.status_code, not_author_test)
