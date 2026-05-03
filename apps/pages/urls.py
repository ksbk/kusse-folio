from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("privacy/", views.PrivacyView.as_view(), name="privacy"),
    path("website-service/", views.WebsiteServiceView.as_view(), name="website_service"),
]
