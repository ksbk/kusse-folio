"""
Management command: seed_services
----------------------------------
Creates the initial set of Service records for the live site.

Usage:
    uv run python manage.py seed_services           # create only (skip existing)
    uv run python manage.py seed_services --reset   # delete all services, then create

Run on production via Railway:
    railway run python manage.py seed_services
"""

from django.core.management.base import BaseCommand

from apps.services.models import Service

SERVICES = [
    {
        "title": "Housing",
        "slug": "housing",
        "summary": (
            "Housing projects shaped by site conditions, planning constraints, and long-term liveability."
        ),
        "description": "",
        "who_for": (
            "Developers, housing associations, institutions, and private clients delivering apartment buildings, infill housing, or residential work."
        ),
        "value_proposition": (
            "Clear housing design that balances site conditions, planning constraints, and day-to-day use without overstatement."
        ),
        "deliverables": (
            "Site and massing studies\n"
            "Planning package\n"
            "Developed design\n"
            "Technical coordination\n"
            "Construction information"
        ),
        "order": 1,
        "active": True,
    },
    {
        "title": "Civic",
        "slug": "civic",
        "summary": (
            "Public-facing buildings shaped by threshold, circulation, durability, and a clear relationship between civic use and context."
        ),
        "description": "",
        "who_for": (
            "Municipal bodies, trusts, cultural organisations, and public-sector clients commissioning libraries, community facilities, and civic buildings."
        ),
        "value_proposition": (
            "Buildings that support everyday public use with clarity, resilience, and a calm architectural presence."
        ),
        "deliverables": (
            "Brief development\n"
            "Concept design\n"
            "Public consultation support\n"
            "Technical package\n"
            "Consultant coordination"
        ),
        "order": 2,
        "active": True,
    },
    {
        "title": "Workplace",
        "slug": "workplace",
        "summary": (
            "Workplace projects where frontage, efficiency, envelope performance, and spatial legibility need to work together."
        ),
        "description": "",
        "who_for": (
            "Commercial clients and development teams delivering office buildings, service buildings, or mixed-use workplace environments."
        ),
        "value_proposition": (
            "A design process that keeps the building useful, robust, and recognisable without forcing an unnecessary brand layer onto the architecture."
        ),
        "deliverables": (
            "Feasibility and frontage studies\n"
            "Developed design\n"
            "Envelope coordination\n"
            "Technical documentation"
        ),
        "order": 3,
        "active": True,
    },
]


class Command(BaseCommand):
    help = "Seed the initial set of Service records."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all existing Service records before seeding.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            deleted, _ = Service.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing service(s)."))

        created = 0
        skipped = 0
        for data in SERVICES:
            _, was_created = Service.objects.get_or_create(
                slug=data["slug"],
                defaults=data,
            )
            if was_created:
                created += 1
            else:
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done — {created} service(s) created, {skipped} already existed."
            )
        )
