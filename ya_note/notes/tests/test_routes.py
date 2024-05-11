from http import HTTPStatus

from .conftest import TestFixtures


class TestRoutes(TestFixtures):
    def test_routes_anonimous(self):
        """Проеряем доступности страниц для анонимного пользователя."""
        ulrs_for_anonimous_with_code_200 = (
            self.home_url,
            self.login_url,
            self.logout_url,
            self.signup_url
        )
        for url in self.urls_for_tests:
            with self.subTest(name=url):
                if url in ulrs_for_anonimous_with_code_200:
                    response = self.anonimous.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    response = self.anonimous.get(url)
                    self.assertRedirects(
                        response,
                        f'{self.login_url}?next={url}'
                    )

    def test_routes_author_client(self):
        """Проверяем доступность страниц для автора заметки."""
        for url in self.urls_for_tests:
            with self.subTest(name=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code,
                                 HTTPStatus.OK)

    def test_routes_not_author_client(self):
        """Проверяем доступность страниц для не автора заметки."""
        ulrs_for_not_author_with_code_404 = (
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        for url in self.urls_for_tests:
            with self.subTest(name=url):
                if url in ulrs_for_not_author_with_code_404:
                    response = self.not_author_client.get(url)
                    self.assertEqual(response.status_code,
                                     HTTPStatus.NOT_FOUND)
                else:
                    response = self.not_author_client.get(url)
                    self.assertEqual(response.status_code,
                                     HTTPStatus.OK)
