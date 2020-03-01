from django import forms
from django.utils.translation import gettext as _

from .models import Item, Location, Category

class ItemEditForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ['name', 'description', 'amount', 'location', 'category', 'barcode']
        labels = {
            'name': _("Name"),
            'description': _("Description"),
            'amount': _("Amount"),
            'location': _("Location"),
            'category': _("Category"),
            'barcode': _("Barcode"),
        }


class ItemLendForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ['lent_to']

        
class LocationEditForm(forms.ModelForm):

    class Meta:
        model = Location
        fields = ['name', 'description', 'parent']


class CategoryEditForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ['name', 'description', 'parent']

class LocationUuidEditForm(forms.ModelForm):

    class Meta:
        model = Location
        fields = ['uuid']
