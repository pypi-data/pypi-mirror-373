from netbox.filtersets import NetBoxModelFilterSet
from .models import Sitemaps


# class SitemapsFilterSet(NetBoxModelFilterSet):
#
#     class Meta:
#         model = Sitemaps
#         fields = ['name', ]
#
#     def search(self, queryset, name, value):
#         return queryset.filter(description__icontains=value)
