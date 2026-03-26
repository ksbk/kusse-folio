"""
Model tests for apps.projects: Project, ProjectImage, Testimonial.
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.projects.models import Project, ProjectImage, Testimonial


@pytest.mark.django_db
def test_project_str(project):
    assert str(project) == "Test House"


@pytest.mark.django_db
def test_project_slug_auto_generated():
    p = Project.objects.create(title="My New House")
    assert p.slug == "my-new-house"


@pytest.mark.django_db
def test_project_get_absolute_url(project):
    url = project.get_absolute_url()
    assert url == f"/projects/{project.slug}/"


@pytest.mark.django_db
def test_project_seo_title_defaults_to_title(project):
    assert project.get_seo_title() == project.title


@pytest.mark.django_db
def test_project_seo_title_uses_custom_when_set(project):
    project.seo_title = "Custom SEO Title"
    project.save()
    assert project.get_seo_title() == "Custom SEO Title"


@pytest.mark.django_db
def test_project_image_fk(project):
    img = ProjectImage.objects.create(
        project=project,
        caption="Facade view",
        order=1,
        image_type="gallery",
    )
    assert img.project == project
    assert project.images.count() == 1


@pytest.mark.django_db
def test_project_preview_image_prefers_cover(project):
    project.cover_image = SimpleUploadedFile("cover.jpg", b"cover-bytes", content_type="image/jpeg")
    project.save()
    gallery = ProjectImage.objects.create(
        project=project,
        image=SimpleUploadedFile("gallery.jpg", b"gallery-bytes", content_type="image/jpeg"),
        alt_text="Gallery alt",
        order=1,
        image_type="gallery",
    )

    assert project.preview_image.name == project.cover_image.name
    assert project.preview_image_alt == project.title
    assert project.preview_gallery_image == gallery


@pytest.mark.django_db
def test_project_preview_image_falls_back_to_first_gallery(project):
    first = ProjectImage.objects.create(
        project=project,
        image=SimpleUploadedFile("first.jpg", b"first-gallery", content_type="image/jpeg"),
        alt_text="First gallery alt",
        order=1,
        image_type="gallery",
    )
    ProjectImage.objects.create(
        project=project,
        image=SimpleUploadedFile("second.jpg", b"second-gallery", content_type="image/jpeg"),
        alt_text="Second gallery alt",
        order=2,
        image_type="gallery",
    )

    assert project.preview_gallery_image == first
    assert project.preview_image.name == first.image.name
    assert project.preview_image_alt == "First gallery alt"


@pytest.mark.django_db
def test_project_preview_image_is_none_without_cover_or_gallery(project):
    assert project.preview_gallery_image is None
    assert project.preview_image is None
    assert project.preview_image_alt == project.title


# ---------------------------------------------------------------------------
# Testimonial
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_testimonial_str(db):
    t = Testimonial.objects.create(
        name="Jane Doe",
        quote="Excellent work.",
        order=1,
        active=True,
    )
    assert "Jane Doe" in str(t)


@pytest.mark.django_db
def test_testimonial_optional_project_fk(db, project):
    t = Testimonial.objects.create(
        name="Client",
        quote="Great.",
        project=project,
        order=1,
        active=True,
    )
    assert t.project == project


@pytest.mark.django_db
def test_testimonial_inactive_excluded_from_active_filter(db):
    Testimonial.objects.create(name="Visible", quote="Good work.", order=1, active=True)
    Testimonial.objects.create(name="Hidden", quote="Not shown.", order=2, active=False)
    active = list(Testimonial.objects.filter(active=True))
    names = [t.name for t in active]
    assert "Visible" in names
    assert "Hidden" not in names


# ---------------------------------------------------------------------------
# ProjectImage.get_alt_text
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_project_image_get_alt_text_uses_alt_text_when_set(project):
    img = ProjectImage.objects.create(
        project=project,
        caption="Entrance facade",
        alt_text="View of the north-facing facade at dusk",
        order=1,
    )
    assert img.get_alt_text() == "View of the north-facing facade at dusk"


@pytest.mark.django_db
def test_project_image_get_alt_text_falls_back_to_caption(project):
    img = ProjectImage.objects.create(
        project=project,
        caption="Entrance facade",
        alt_text="",
        order=1,
    )
    assert img.get_alt_text() == "Entrance facade"


@pytest.mark.django_db
def test_project_image_get_alt_text_falls_back_to_project_title(project):
    img = ProjectImage.objects.create(
        project=project,
        caption="",
        alt_text="",
        order=1,
    )
    assert img.get_alt_text() == project.title


# ---------------------------------------------------------------------------
# Project.updated_at
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_project_updated_at_is_set_on_save(project):
    assert project.updated_at is not None


@pytest.mark.django_db
def test_project_updated_at_changes_on_resave(project):
    first = project.updated_at
    project.title = "Test House (Updated)"
    project.save()
    project.refresh_from_db()
    assert project.updated_at >= first


@pytest.mark.django_db
def test_project_image_str(project):
    img = ProjectImage.objects.create(project=project, order=5, caption="Roof terrace")
    assert str(img) == "Test House — image 5"
