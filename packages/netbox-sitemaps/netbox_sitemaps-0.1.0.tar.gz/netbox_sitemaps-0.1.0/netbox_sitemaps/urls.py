from django.urls import path
from netbox.views.generic import ObjectChangeLogView

from . import models, views


urlpatterns = (
    path("sitemapss/", views.SitemapsListView.as_view(), name="sitemaps_list"),
    path("sitemapss/add/", views.SitemapsEditView.as_view(), name="sitemaps_add"),
    path("sitemapss/<int:pk>/", views.SitemapsView.as_view(), name="sitemaps"),
    path("sitemapss/<int:pk>/edit/", views.SitemapsEditView.as_view(), name="sitemaps_edit"),
    path("sitemapss/<int:pk>/delete/", views.SitemapsDeleteView.as_view(), name="sitemaps_delete"),
    path(
        "sitemapss/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="sitemaps_changelog",
        kwargs={"model": models.Sitemaps},
    ),
)
