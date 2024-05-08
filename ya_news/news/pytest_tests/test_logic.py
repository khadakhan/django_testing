from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client,
                                            news,
                                            detail_url,
                                            form_data):
    """Анонимный пользователь не может создать комментарий."""
    comments_count_before_post = Comment.objects.count()
    client.post(detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before_post


def test_user_can_create_comment(author_client,
                                 news,
                                 detail_url,
                                 author,
                                 form_data,):
    """Авторизованный пользователь может создать комментарий."""
    comments_count_before_post = Comment.objects.count()
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1 + comments_count_before_post
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client,
                                 detail_url,
                                 news):
    """Проверка блокировки стоп-слов."""
    comments_count_before_post = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before_post


def test_author_can_delete_comment(author_client,
                                   comment,
                                   delete_url,
                                   detail_url,
                                   news):
    """Автор может удалять свой комментарий."""
    comments_count_before_delete = Comment.objects.count()
    url_to_comments = f'{detail_url}#comments'
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before_delete - 1


def test_user_cant_delete_comment_of_another_user(not_author_client,
                                                  delete_url,
                                                  comment):
    """Не автор не может удалять свой комментарий."""
    comments_count_before_delete = Comment.objects.count()
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before_delete


def test_author_can_edit_comment(news,
                                 author,
                                 author_client,
                                 edit_url,
                                 detail_url,
                                 form_data,
                                 comment):
    """Автор может редактировать свой комментарий."""
    comments_count_before_edit = Comment.objects.count()
    url_to_comments = f'{detail_url}#comments'
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author
    comments_count = Comment.objects.count()
    assert comments_count_before_edit == comments_count


def test_user_cant_edit_comment_of_another_user(not_author_client,
                                                news,
                                                author,
                                                edit_url,
                                                form_data,
                                                comment):
    """Не автор не может редактировать свой комментарий."""
    comments_count_before_edit = Comment.objects.count()
    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment = Comment.objects.get()
    assert comment.text != form_data['text']
    assert comment.news == news
    assert comment.author == author
    comments_count = Comment.objects.count()
    assert comments_count_before_edit == comments_count
