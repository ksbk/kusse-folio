import re

import pytest

playwright = pytest.importorskip("playwright.sync_api")
expect = playwright.expect

pytestmark = pytest.mark.e2e


def test_projects_list_filter_and_card_navigation(
    mobile_page, open_page, app_url, site_settings, project_factory
):
    page = mobile_page
    project_factory(title="Test House", category="housing")
    project_factory(title="Office Fitout", category="workplace")

    open_page("/projects/")

    expect(page.get_by_role("heading", name="Projects", level=1)).to_be_visible()

    filter_nav = page.get_by_role("navigation", name="Filter projects by category")
    expect(filter_nav.get_by_role("link", name="Housing", exact=True)).to_be_visible()
    expect(filter_nav.get_by_role("link", name="Workplace", exact=True)).to_be_visible()
    expect(filter_nav.get_by_role("link", name="Civic", exact=True)).to_have_count(0)
    expect(filter_nav.get_by_role("link", name="Interiors", exact=True)).to_have_count(0)
    expect(filter_nav.get_by_role("link", name="Renovation", exact=True)).to_have_count(0)

    housing_filter = filter_nav.get_by_role("link", name="Housing", exact=True)
    housing_filter.click()

    expect(page).to_have_url(f"{app_url}/projects/?category=housing")
    expect(housing_filter).to_have_attribute("aria-current", "page")
    expect(page.get_by_role("heading", name="Test House")).to_be_visible()
    expect(page.get_by_role("heading", name="Office Fitout")).to_have_count(0)

    page.get_by_role("link", name=re.compile("Test House")).first.click()

    expect(page.get_by_role("heading", name="Test House", level=1)).to_be_visible()
