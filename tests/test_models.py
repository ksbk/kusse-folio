"""
Model unit tests — instantiation, basic relations, and singleton behaviour.
"""

import pytest

from contact.models import ContactInquiry
from portfolio.models import AboutProfile, Service, SiteSettings
from projects.models import Project, ProjectImage, Testimonial

# ---------------------------------------------------------------------------
# SiteSettings singleton
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_site_settings_singleton_load_creates_row():
    obj = SiteSettings.load()
    assert obj.pk == 1


@pytest.mark.django_db
def test_site_settings_singleton_only_one_row():
    SiteSettings.load()
    SiteSettings.load()  # second call must not create a second row
    assert SiteSettings.objects.count() == 1


@pytest.mark.django_db
def test_site_settings_saves_with_pk_1():
    s = SiteSettings(site_name="Test")
    s.save()
    assert s.pk == 1


# ---------------------------------------------------------------------------
# AboutProfile singleton
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_about_profile_singleton():
    a = AboutProfile.load()
    b = AboutProfile.load()
    assert a.pk == b.pk == 1
    assert AboutProfile.objects.count() == 1


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# ProjectImage — FK relation
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_service_str(service):
    assert str(service) == "Architectural Design"


@pytest.mark.django_db
def test_service_slug_auto_generated():
    s = Service.objects.create(title="Urban Planning", order=10, active=True)
    assert s.slug == "urban-planning"


@pytest.mark.django_db
def test_service_deliverables_list(db):
    s = Service.objects.create(
        title="Test Service",
        order=1,
        active=True,
        deliverables="Item one\nItem two\nItem three",
    )
    items = s.deliverables_list()
    assert len(items) == 3
    assert "Item one" in items


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


# ---------------------------------------------------------------------------
# ContactInquiry
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_contact_inquiry_default_status(db):
    inq = ContactInquiry.objects.create(
        name="Alice",
        email="alice@example.com",
        message="Hello, I'd like to enquire.",
    )
    assert inq.status == "new"
    assert "Alice" in str(inq)


# ---------------------------------------------------------------------------
# New field: ProjectImage.get_alt_text
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
# New field: Project.updated_at
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


# ---------------------------------------------------------------------------
# New field: SiteSettings social/og fields
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_site_settings_new_social_fields_default_blank():
    s = SiteSettings.load()
    assert s.behance_url == ""
    assert s.issuu_url == ""
    assert s.og_image.name is None or s.og_image.name == ""
