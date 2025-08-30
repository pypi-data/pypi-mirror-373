from django.db.models import Count

from netbox.views import generic
from . import filtersets, forms, models, tables


class SitemapsView(generic.ObjectView):
    queryset = models.Sitemaps.objects.all()


class SitemapsListView(generic.ObjectListView):
    queryset = models.Sitemaps.objects.all()
    table = tables.SitemapsTable


class SitemapsEditView(generic.ObjectEditView):
    queryset = models.Sitemaps.objects.all()
    form = forms.SitemapsForm


class SitemapsDeleteView(generic.ObjectDeleteView):
    queryset = models.Sitemaps.objects.all()
