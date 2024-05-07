import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, all_news):
    """Проверяем, что количество новостей на домашней странице
    ограничивается константой NEWS_COUNT_ON_HOME_PAGE.
    """
    response = client.get(reverse('news:home'))
    assert (
        response.context['object_list']
        .count() == settings.NEWS_COUNT_ON_HOME_PAGE
    )


@pytest.mark.django_db
def test_news_order(client):
    """Проверяем порядок вывода списка новостей на
    домашней странице.
    """
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, all_comments):
    """Проверяем порядок отображения комментариев."""
    response = client.get(reverse('news:detail',
                                  args=(news.pk,)))
    assert 'news' in response.context
    news = response.context['news']
    comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news):
    """Проверяем, что анонимный пользователь не видит форму
    для комментария
    """
    response = client.get(reverse('news:detail',
                                  args=(news.pk,)))
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, news):
    """Проверяем, что авторизованный пользователь видит
    форму для комментария
    """
    response = author_client.get(reverse('news:detail',
                                         args=(news.pk,)))
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
