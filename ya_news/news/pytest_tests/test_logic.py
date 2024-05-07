import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client,
                                            pk_for_news_args,
                                            form_data):
    """Анонимный пользователь не может создать комментарий."""
    url = reverse('news:detail', args=pk_for_news_args)
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(author_client,
                                 news,
                                 author,
                                 pk_for_news_args,
                                 form_data,):
    """Авторизованный пользователь может создать комментарий."""
    url = reverse('news:detail', args=pk_for_news_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client,
                                 pk_for_news_args):
    """Проверка блокировки стоп-слов."""
    url = reverse('news:detail', args=pk_for_news_args)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client,
                                   pk_for_comment_args,
                                   pk_for_news_args,
                                   ):
    """Автор может удалять свой комментарий."""
    delete_url = reverse('news:delete', args=pk_for_comment_args)
    url_to_comments = reverse('news:detail',
                              args=pk_for_news_args) + '#comments'
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(not_author_client,
                                                  pk_for_comment_args,
                                                  ):
    """Не автор не может удалять свой комментарий."""
    delete_url = reverse('news:delete', args=pk_for_comment_args)
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can_edit_comment(pk_for_comment_args,
                                 pk_for_news_args,
                                 author_client,
                                 form_data,
                                 comment):
    """Автор может редактировать свой комментарий."""
    edit_url = reverse('news:edit', args=pk_for_comment_args)
    url_to_comments = reverse('news:detail',
                              args=pk_for_news_args) + '#comments'
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(not_author_client,
                                                pk_for_comment_args,
                                                form_data,
                                                comment):
    """Не автор не может редактировать свой комментарий."""
    edit_url = reverse('news:edit', args=pk_for_comment_args)
    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'
