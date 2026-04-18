"""Shared enquiry vocabulary for project, service, and contact surfaces."""

PROJECT_TYPE_CHOICES = [
    ("", "Select project type..."),
    ("Housing", "Housing"),
    ("Civic", "Civic"),
    ("Workplace", "Workplace"),
    ("Renovation / Adaptive Reuse", "Renovation / Adaptive Reuse"),
    ("Other", "Other"),
]

LEGACY_PROJECT_TYPE_MAP = {
    "Residential Design": "Housing",
    "Commercial Design": "Workplace",
    "Interior Architecture": "Other",
    "Concept Development": "Other",
    "3D Visualisation": "Other",
    "Planning & Consultation": "Other",
    "Renovation / Adaptive Reuse": "Renovation / Adaptive Reuse",
}
