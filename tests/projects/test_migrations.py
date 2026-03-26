import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

LATEST_PROJECTS_MIGRATION = "0003_simplify_project_taxonomy"


def migrate_projects_to(target):
    executor = MigrationExecutor(connection)
    executor.loader.build_graph()
    targets = [
        node for node in executor.loader.graph.leaf_nodes() if node[0] != "projects"
    ]
    targets.append(("projects", target))
    executor.migrate(targets)
    return executor.loader.project_state(targets).apps


@pytest.mark.django_db(transaction=True)
def test_project_taxonomy_migration_remaps_supported_legacy_categories():
    old_apps = migrate_projects_to("0002_clean_category_choices")
    Project = old_apps.get_model("projects", "Project")

    Project.objects.create(title="Housing Project", slug="housing-project", short_description="Demo", category="residential")
    Project.objects.create(title="Civic Project", slug="civic-project", short_description="Demo", category="cultural")
    Project.objects.create(title="Workplace Project", slug="workplace-project", short_description="Demo", category="commercial")

    new_apps = migrate_projects_to(LATEST_PROJECTS_MIGRATION)
    Project = new_apps.get_model("projects", "Project")

    categories = sorted(Project.objects.values_list("category", flat=True))
    assert categories == ["civic", "housing", "workplace"]


@pytest.mark.django_db(transaction=True)
def test_project_taxonomy_migration_fails_when_removed_legacy_categories_remain():
    old_apps = migrate_projects_to("0002_clean_category_choices")
    Project = old_apps.get_model("projects", "Project")

    Project.objects.create(
        title="Interior Retrofit",
        slug="interior-retrofit",
        short_description="Demo",
        category="interior",
    )

    try:
        with pytest.raises(RuntimeError, match="Unsupported legacy project categories remain"):
            migrate_projects_to(LATEST_PROJECTS_MIGRATION)
    finally:
        Project.objects.all().delete()
        migrate_projects_to(LATEST_PROJECTS_MIGRATION)
