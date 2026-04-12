"""Shared enquiry vocabulary for project, service, and contact surfaces."""

PROJECT_TYPE_CHOICES = [
    ("", "Select project type..."),
    ("Housing", "Housing"),
    ("Civic", "Civic"),
    ("Workplace", "Workplace"),
    ("Renovation / Adaptive Reuse", "Renovation / Adaptive Reuse"),
    ("Other", "Other"),
]

PROJECT_CATEGORY_TO_ENQUIRY_TYPE = {
    "housing": "Housing",
    "civic": "Civic",
    "workplace": "Workplace",
}

SERVICE_SLUG_TO_ENQUIRY_TYPE = {
    "housing": "Housing",
    "residential-design": "Housing",
    "civic": "Civic",
    "civic-community-buildings": "Civic",
    "workplace": "Workplace",
    "workplace-commercial-buildings": "Workplace",
    "renovation-adaptive-reuse": "Renovation / Adaptive Reuse",
    "interior-architecture": "Other",
    "concept-design": "Other",
}

LEGACY_PROJECT_TYPE_MAP = {
    "Residential Design": "Housing",
    "Commercial Design": "Workplace",
    "Interior Architecture": "Other",
    "Concept Development": "Other",
    "3D Visualisation": "Other",
    "Planning & Consultation": "Other",
    "Renovation / Adaptive Reuse": "Renovation / Adaptive Reuse",
}
