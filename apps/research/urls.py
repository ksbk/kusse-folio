from django.urls import path

from . import views

app_name = "research"

urlpatterns = [
    path("", views.ResearchListView.as_view(), name="list"),
    path("<slug:slug>/", views.ResearchDetailView.as_view(), name="detail"),
]
