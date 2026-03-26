"""
View tests for apps.pages: home and about pages.
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.projects.models import Project, ProjectImage


@pytest.mark.django_db
def test_home_page(client, site_settings):
    response = client.get(reverse("pages:home"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_about_page(client, site_settings):
    response = client.get(reverse("pages:about"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_privacy_page(client, site_settings):
    response = client.get(reverse("pages:privacy"))
    assert response.status_code == 200
    assert b"Privacy" in response.content


@pytest.mark.django_db
def test_homepage_projects_merge_featured_and_supporting_work(client, site_settings):
    """Homepage projects should show featured work first, then fill from supporting work."""
    featured_one = Project.objects.create(
        title="Featured One",
        slug="featured-one",
        short_description="Featured project.",
        category="workplace",
        status="completed",
        featured=True,
        order=2,
    )
    featured_two = Project.objects.create(
        title="Featured Two",
        slug="featured-two",
        short_description="Featured project.",
        category="civic",
        status="completed",
        featured=True,
        order=1,
    )
    supporting_one = Project.objects.create(
        title="Supporting One",
        slug="supporting-one",
        short_description="Supporting project.",
        category="housing",
        status="completed",
        featured=False,
        order=3,
    )
    supporting_two = Project.objects.create(
        title="Supporting Two",
        slug="supporting-two",
        short_description="Supporting project.",
        category="housing",
        status="completed",
        featured=False,
        order=4,
    )
    supporting_three = Project.objects.create(
        title="Supporting Three",
        slug="supporting-three",
        short_description="Supporting project.",
        category="housing",
        status="completed",
        featured=False,
        order=5,
    )

    response = client.get(reverse("pages:home"))

    assert response.status_code == 200
    project_slugs = [p.slug for p in response.context["homepage_projects"]]
    assert project_slugs == [
        featured_two.slug,
        featured_one.slug,
        supporting_one.slug,
        supporting_two.slug,
    ]
    assert supporting_three.slug not in project_slugs


@pytest.mark.django_db
def test_home_testimonials_in_context(client, site_settings):
    response = client.get(reverse("pages:home"))
    assert response.status_code == 200
    assert "testimonials" in response.context


@pytest.mark.django_db
def test_home_testimonials_excludes_inactive(client, site_settings):
    from apps.projects.models import Testimonial

    Testimonial.objects.create(name="Shown", quote="Great.", order=1, active=True)
    Testimonial.objects.create(name="Hidden", quote="Not shown.", order=2, active=False)
    response = client.get(reverse("pages:home"))
    names = [t.name for t in response.context["testimonials"]]
    assert "Shown" in names
    assert "Hidden" not in names


@pytest.mark.django_db
def test_home_project_cards_fall_back_to_first_gallery_image(client, site_settings):
    featured = Project.objects.create(
        title="Hero Project",
        slug="hero-project",
        short_description="Lead project.",
        category="workplace",
        status="completed",
        featured=True,
        cover_image=SimpleUploadedFile("hero.jpg", b"hero-image", content_type="image/jpeg"),
    )
    fallback_project = Project.objects.create(
        title="Gallery Preview Project",
        slug="gallery-preview-project",
        short_description="Uses a gallery image on cards.",
        category="housing",
        status="completed",
        featured=True,
    )
    gallery_image = ProjectImage.objects.create(
        project=fallback_project,
        image=SimpleUploadedFile("preview.jpg", b"preview-image", content_type="image/jpeg"),
        alt_text="Preview facade",
        order=1,
        image_type="gallery",
    )

    response = client.get(reverse("pages:home"))

    assert response.status_code == 200
    assert featured.cover_image.url.encode() in response.content
    assert gallery_image.image.url.encode() in response.content
    assert b"project-card__placeholder" not in response.content


@pytest.mark.django_db
def test_homepage_uses_selected_projects_strip_and_updated_cta(client, site_settings):
    Project.objects.create(
        title="Selected Project",
        slug="selected-project",
        short_description="Homepage project.",
        category="workplace",
        status="completed",
        featured=True,
        order=1,
    )

    response = client.get(reverse("pages:home"))

    assert response.status_code == 200
    assert b"Selected Projects" in response.content
    assert b"Housing, civic, and workplace projects from the studio" in response.content
    assert b"More Work" not in response.content
    assert b"Who We Work With" in response.content
    assert b"Project Types" in response.content
    assert b"How Work Starts" in response.content
    assert b"Start a Conversation" in response.content


@pytest.mark.django_db
def test_footer_includes_privacy_link(client, site_settings):
    response = client.get(reverse("pages:home"))

    assert response.status_code == 200
    assert reverse("pages:privacy").encode() in response.content
    assert b"Privacy" in response.content
