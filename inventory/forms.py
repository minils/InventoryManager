from django import forms

from .models import Item, Location, Category

class ItemEditForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ['name', 'description', 'amount', 'location', 'category', 'barcode']


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
