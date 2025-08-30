from django import forms
from ipam.models import Prefix
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField

from .models import Sitemaps


class SitemapsForm(NetBoxModelForm):
    class Meta:
        model = Sitemaps
        fields = ("name", "tags")
