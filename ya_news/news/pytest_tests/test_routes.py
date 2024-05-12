from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db

HOME_URL = pytest.lazy_fixture('home_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
LOGOUT_URL = pytest.lazy_fixture('logout_url')
SIGNUP_URL = pytest.lazy_fixture('signup_url')
DETAIL_URL = pytest.lazy_fixture('detail_url')
EDIT_URL = pytest.lazy_fixture('edit_url')
DELETE_URL = pytest.lazy_fixture('delete_url')
ANONIMOUS = pytest.lazy_fixture('client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
NOT_AUTHOR_CLIENT = pytest.lazy_fixture('not_author_client')


@pytest.mark.parametrize(
    'url, client_type, status_code',
    ((HOME_URL, ANONIMOUS, HTTPStatus.OK),
     (DETAIL_URL, ANONIMOUS, HTTPStatus.OK),
     (LOGIN_URL, ANONIMOUS, HTTPStatus.OK),
     (LOGOUT_URL, ANONIMOUS, HTTPStatus.OK),
     (SIGNUP_URL, ANONIMOUS, HTTPStatus.OK),
     (EDIT_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
     (EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
     (DELETE_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
     (DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK))
)
def test_home_availability_for_anonymous_user(url, client_type, status_code):
    """Проверяем доступность страниц для анонимного пользователя.
    Проверяем доступность редактирования и удаления комментария
    для автора и не автора.
    """
    response = client_type.get(url)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    'url',
    (EDIT_URL, DELETE_URL)
)
def test_redirects(client, login_url, url):
    """Проверяем перенаправление анонимного пользователя на страницу входа."""
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
