import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client, home_url, all_news):
    """Проверяем ограничение количество новостей.
    Количество ограничивается константой NEWS_COUNT_ON_HOME_PAGE.
    """
    response = client.get(home_url)
    assert (
        response.context['object_list']
        .count() == settings.NEWS_COUNT_ON_HOME_PAGE
    )


def test_news_order(client, home_url):
    """Проверяем порядок вывода списка новостей."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news, detail_url, all_comments):
    """Проверяем порядок отображения комментариев."""
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, detail_url, news):
    """Анонимный пользователь не видит форму для комментария."""
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, detail_url, news):
    """Авторизованный пользователь видит форму для комментария."""
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
