from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, client_type, status_code',
    (
        (pytest.lazy_fixture('home_url'), pytest.lazy_fixture('client'),
         HTTPStatus.OK),
        (pytest.lazy_fixture('detail_url'), pytest.lazy_fixture('client'),
         HTTPStatus.OK),
        (pytest.lazy_fixture('login_url'), pytest.lazy_fixture('client'),
         HTTPStatus.OK),
        (pytest.lazy_fixture('logout_url'), pytest.lazy_fixture('client'),
         HTTPStatus.OK),
        (pytest.lazy_fixture('signup_url'), pytest.lazy_fixture('client'),
         HTTPStatus.OK),
        (pytest.lazy_fixture('edit_url'),
         pytest.lazy_fixture('not_author_client'),
         HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('edit_url'),
         pytest.lazy_fixture('author_client'),
         HTTPStatus.OK),
        (pytest.lazy_fixture('delete_url'),
         pytest.lazy_fixture('not_author_client'),
         HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('delete_url'),
         pytest.lazy_fixture('author_client'),
         HTTPStatus.OK),
    )
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
    (pytest.lazy_fixture('edit_url'), pytest.lazy_fixture('delete_url'))
)
def test_redirects(client, login_url, url):
    """Проверяем перенаправление анонимного пользователя на страницу входа."""
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
