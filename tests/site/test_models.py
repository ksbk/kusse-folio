"""
Model tests for apps.site: SiteSettings and AboutProfile singletons.
"""

import pytest

from apps.site.models import AboutProfile, SiteSettings

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
# SiteSettings — social / og fields
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_site_settings_new_social_fields_default_blank():
    s = SiteSettings.load()
    assert s.behance_url == ""
    assert s.issuu_url == ""
    assert s.og_image.name is None or s.og_image.name == ""


@pytest.mark.django_db
def test_site_settings_str():
    s = SiteSettings.load()
    assert str(s) == "Site Settings"


@pytest.mark.django_db
def test_about_profile_str():
    a = AboutProfile.load()
    assert str(a) == "About Profile"


# ---------------------------------------------------------------------------
# SiteSettings — homepage project count fields
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_site_settings_homepage_project_count_defaults():
    s = SiteSettings.load()
    assert s.homepage_projects_mobile_count == 3
    assert s.homepage_projects_tablet_count == 4
    assert s.homepage_projects_desktop_count == 6


@pytest.mark.django_db
def test_site_settings_homepage_project_count_rejects_out_of_range():
    from django.core.exceptions import ValidationError

    s = SiteSettings.load()
    s.homepage_projects_mobile_count = 0
    with pytest.raises(ValidationError) as exc_info:
        s.clean()
    assert "homepage_projects_mobile_count" in exc_info.value.message_dict

    s2 = SiteSettings.load()
    s2.homepage_projects_desktop_count = 7
    with pytest.raises(ValidationError) as exc_info2:
        s2.clean()
    assert "homepage_projects_desktop_count" in exc_info2.value.message_dict


@pytest.mark.django_db
def test_site_settings_homepage_project_count_rejects_mobile_greater_than_tablet():
    from django.core.exceptions import ValidationError

    s = SiteSettings.load()
    s.homepage_projects_mobile_count = 5
    s.homepage_projects_tablet_count = 3
    s.homepage_projects_desktop_count = 6
    with pytest.raises(ValidationError) as exc_info:
        s.clean()
    assert "homepage_projects_mobile_count" in exc_info.value.message_dict


@pytest.mark.django_db
def test_site_settings_homepage_project_count_rejects_tablet_greater_than_desktop():
    from django.core.exceptions import ValidationError

    s = SiteSettings.load()
    s.homepage_projects_mobile_count = 2
    s.homepage_projects_tablet_count = 5
    s.homepage_projects_desktop_count = 3
    with pytest.raises(ValidationError) as exc_info:
        s.clean()
    assert "homepage_projects_tablet_count" in exc_info.value.message_dict


@pytest.mark.django_db
def test_site_settings_homepage_project_count_accepts_valid_values():
    from django.core.exceptions import ValidationError

    s = SiteSettings.load()
    s.homepage_projects_mobile_count = 2
    s.homepage_projects_tablet_count = 4
    s.homepage_projects_desktop_count = 6
    # Should not raise
    try:
        s.clean()
    except ValidationError:
        pytest.fail("clean() raised ValidationError for valid counts 2/4/6")


# ---------------------------------------------------------------------------
# SiteSettings — hero fields
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_site_settings_hero_label_defaults_blank():
    s = SiteSettings.load()
    assert s.hero_label == ""


@pytest.mark.django_db
def test_site_settings_hero_compact_defaults_false():
    s = SiteSettings.load()
    assert s.hero_compact is False


@pytest.mark.django_db
def test_site_settings_nav_name_defaults_blank():
    s = SiteSettings.load()
    assert s.nav_name == ""


@pytest.mark.django_db
def test_site_settings_portfolio_preset_defaults_generic():
    s = SiteSettings.load()
    assert s.portfolio_preset == SiteSettings.PortfolioPreset.GENERIC


@pytest.mark.django_db
def test_site_settings_blog_enabled_defaults_false():
    s = SiteSettings.load()
    assert s.blog_enabled is False


# ---------------------------------------------------------------------------
# SiteSettings — optional module flags
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_site_settings_services_enabled_defaults_false():
    s = SiteSettings.load()
    assert s.services_enabled is False


@pytest.mark.django_db
def test_site_settings_testimonials_enabled_defaults_false():
    s = SiteSettings.load()
    assert s.testimonials_enabled is False


@pytest.mark.django_db
def test_site_settings_services_enabled_can_be_set():
    s = SiteSettings.load()
    s.services_enabled = True
    s.save()
    refreshed = SiteSettings.load()
    assert refreshed.services_enabled is True


@pytest.mark.django_db
def test_site_settings_testimonials_enabled_can_be_set():
    s = SiteSettings.load()
    s.testimonials_enabled = True
    s.save()
    refreshed = SiteSettings.load()
    assert refreshed.testimonials_enabled is True


@pytest.mark.django_db
def test_site_settings_research_enabled_defaults_false():
    s = SiteSettings.load()
    assert s.research_enabled is False


@pytest.mark.django_db
def test_site_settings_publications_enabled_defaults_false():
    s = SiteSettings.load()
    assert s.publications_enabled is False


@pytest.mark.django_db
def test_site_settings_resume_enabled_defaults_false():
    s = SiteSettings.load()
    assert s.resume_enabled is False


@pytest.mark.django_db
def test_site_settings_research_enabled_can_be_set():
    s = SiteSettings.load()
    s.research_enabled = True
    s.save()
    assert SiteSettings.load().research_enabled is True


@pytest.mark.django_db
def test_site_settings_publications_enabled_can_be_set():
    s = SiteSettings.load()
    s.publications_enabled = True
    s.save()
    assert SiteSettings.load().publications_enabled is True


@pytest.mark.django_db
def test_site_settings_resume_enabled_can_be_set():
    s = SiteSettings.load()
    s.resume_enabled = True
    s.save()
    assert SiteSettings.load().resume_enabled is True


# ---------------------------------------------------------------------------
# ClientProfile
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_client_profile_can_be_created():
    from apps.site.models import ClientProfile
    cp = ClientProfile.objects.create(client_name="Acme Studio", website_domain="acme.example.com")
    assert cp.pk is not None
    assert cp.is_active is True


@pytest.mark.django_db
def test_client_profile_str():
    from apps.site.models import ClientProfile
    cp = ClientProfile.objects.create(client_name="Studio Bravo")
    assert str(cp) == "Studio Bravo"


@pytest.mark.django_db
def test_client_profile_package_type_choices():
    from apps.site.models import ClientProfile
    valid_types = {c[0] for c in ClientProfile.PACKAGE_CHOICES}
    assert "starter" in valid_types
    assert "pro" in valid_types


# ---------------------------------------------------------------------------
# SiteSettings — contact visibility controls (v1.4.0)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_site_settings_show_email_defaults_true():
    s = SiteSettings.load()
    assert s.show_email is True


@pytest.mark.django_db
def test_site_settings_show_phone_defaults_false():
    s = SiteSettings.load()
    assert s.show_phone is False


@pytest.mark.django_db
def test_site_settings_show_location_defaults_true():
    s = SiteSettings.load()
    assert s.show_location is True


@pytest.mark.django_db
def test_site_settings_show_phone_can_be_enabled():
    s = SiteSettings.load()
    s.show_phone = True
    s.save()
    assert SiteSettings.load().show_phone is True


@pytest.mark.django_db
def test_site_settings_show_location_can_be_disabled():
    s = SiteSettings.load()
    s.show_location = False
    s.save()
    assert SiteSettings.load().show_location is False
