"""
View tests for apps.blog: writing list and post detail.
"""

import datetime

import pytest
from django.urls import reverse

from apps.blog.models import Post
from apps.site.models import SocialLink

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _published_post(**kwargs) -> Post:
    defaults = {
        "title": "Test Post",
        "slug": "test-post",
        "summary": "A short summary.",
        "body": "Body text.",
        "published_date": datetime.date(2025, 1, 15),
        "is_published": True,
    }
    defaults.update(kwargs)
    return Post.objects.create(**defaults)


def _draft_post(**kwargs) -> Post:
    defaults = {
        "title": "Draft Post",
        "slug": "draft-post",
        "is_published": False,
    }
    defaults.update(kwargs)
    return Post.objects.create(**defaults)


# ---------------------------------------------------------------------------
# Blog list
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_writing_list_returns_200(client, site_settings):
    response = client.get(reverse("blog:list"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_writing_list_shows_published_posts(client, site_settings):
    _published_post(title="First Post", slug="first-post")
    response = client.get(reverse("blog:list"))
    assert b"First Post" in response.content


@pytest.mark.django_db
def test_writing_list_excludes_draft_posts(client, site_settings):
    _draft_post(title="Secret Draft", slug="secret-draft")
    response = client.get(reverse("blog:list"))
    assert b"Secret Draft" not in response.content


@pytest.mark.django_db
def test_writing_list_shows_empty_state_when_no_posts(client, site_settings):
    response = client.get(reverse("blog:list"))
    assert response.status_code == 200
    assert b"No posts published yet" in response.content


@pytest.mark.django_db
def test_writing_list_shows_summary(client, site_settings):
    _published_post(summary="This is the summary text.")
    response = client.get(reverse("blog:list"))
    assert b"This is the summary text." in response.content


@pytest.mark.django_db
def test_writing_list_orders_by_published_date_descending(client, site_settings):
    _published_post(
        title="Older Post",
        slug="older-post",
        published_date=datetime.date(2024, 6, 1),
    )
    _published_post(
        title="Newer Post",
        slug="newer-post",
        published_date=datetime.date(2025, 3, 1),
    )
    response = client.get(reverse("blog:list"))
    content = response.content.decode()
    assert content.index("Newer Post") < content.index("Older Post")


# ---------------------------------------------------------------------------
# Post detail
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_post_detail_returns_200_for_published_post(client, site_settings):
    post = _published_post()
    response = client.get(reverse("blog:detail", kwargs={"slug": post.slug}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_post_detail_returns_404_for_draft(client, site_settings):
    post = _draft_post()
    response = client.get(reverse("blog:detail", kwargs={"slug": post.slug}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_post_detail_renders_title_and_body(client, site_settings):
    post = _published_post(title="My Essay", body="Essay body here.")
    response = client.get(reverse("blog:detail", kwargs={"slug": post.slug}))
    assert b"My Essay" in response.content
    assert b"Essay body here." in response.content


@pytest.mark.django_db
def test_post_detail_renders_tags(client, site_settings):
    post = _published_post(tags="design, process")
    response = client.get(reverse("blog:detail", kwargs={"slug": post.slug}))
    assert b"design" in response.content
    assert b"process" in response.content


@pytest.mark.django_db
def test_post_detail_breadcrumb_links_to_list(client, site_settings):
    post = _published_post()
    response = client.get(reverse("blog:detail", kwargs={"slug": post.slug}))
    assert b"/writing/" in response.content


# ---------------------------------------------------------------------------
# Post model
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_post_tag_list_splits_comma_separated_tags():
    post = _published_post(tags="design, process, tools")
    assert post.tag_list == ["design", "process", "tools"]


@pytest.mark.django_db
def test_post_tag_list_is_empty_when_no_tags():
    post = _published_post(tags="")
    assert post.tag_list == []


@pytest.mark.django_db
def test_post_slug_is_auto_generated_from_title():
    post = Post.objects.create(
        title="Auto Slug Post",
        is_published=True,
        published_date=datetime.date(2025, 1, 1),
    )
    assert post.slug == "auto-slug-post"


# ---------------------------------------------------------------------------
# SocialLink footer rendering
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_footer_renders_social_links_when_active(client, site_settings):
    SocialLink.objects.create(label="LinkedIn", url="https://linkedin.com/in/test", order=1, active=True)
    response = client.get(reverse("pages:home"))
    assert b"LinkedIn" in response.content
    assert b"https://linkedin.com/in/test" in response.content


@pytest.mark.django_db
def test_footer_excludes_inactive_social_links(client, site_settings):
    SocialLink.objects.create(label="Facebook", url="https://facebook.com/test", order=1, active=False)
    response = client.get(reverse("pages:home"))
    assert b"https://facebook.com/test" not in response.content


@pytest.mark.django_db
def test_footer_falls_back_to_inline_social_when_no_social_links(client, site_settings):
    site_settings.instagram_url = "https://instagram.com/testaccount"
    site_settings.contact_email = "hello@test.com"
    site_settings.save()
    response = client.get(reverse("pages:home"))
    assert b"https://instagram.com/testaccount" in response.content


@pytest.mark.django_db
def test_footer_uses_social_links_over_inline_fields_when_both_present(client, site_settings):
    site_settings.instagram_url = "https://instagram.com/old"
    site_settings.contact_email = "hello@test.com"
    site_settings.save()
    SocialLink.objects.create(label="Instagram", url="https://instagram.com/new", order=1, active=True)
    response = client.get(reverse("pages:home"))
    assert b"https://instagram.com/new" in response.content
    assert b"https://instagram.com/old" not in response.content
