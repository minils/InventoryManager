import logging
from django.utils.datastructures import MultiValueDictKeyError
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views import generic
from django.urls import reverse

from uuid import UUID

from .models import Item, Location, Category
from .forms import LocationEditForm, ItemEditForm, CategoryEditForm

logger = logging.getLogger(__name__)

def index(request):
    latest_items = Item.objects.order_by('-creation_date')[:5]
    categories = Category.objects.order_by('-creation_date')[:5]
    locations = Location.objects.order_by('-creation_date')[:5]
    return render(request, 'inventory/index.html', {
        'latest_items': latest_items,
        'categories': categories,
        'locations': locations,
        'nav_item': 'Home',
    })

class SearchItem(generic.ListView):
    paginate_by = 25
    template_name = 'inventory/search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_term'] = self.request.GET['q']
        context['search_type'] = self.request.GET['type']
        if len(context['search_term']) < 3:
            context['error_message'] = "Search term must contain at least 3 letters."
        return context
    
    def get_queryset(self):
        search_term = self.request.GET['q']
        search_type = self.request.GET['type']
        if len(search_term) < 3:
            return []
        else:
            if search_type == 'item':
                results = Item.objects.filter(name__contains=search_term).order_by('name')
            elif search_type == 'location':
                results = Location.objects.filter(name__contains=search_term).order_by('name')
            elif search_type == 'category':
                results = Category.objects.filter(name__contains=search_term).order_by('name')
            else:
                results = []
            return results

class LocationsView(generic.ListView):
    model = Location
    paginate_by = 25


class LocationUuidView(generic.DetailView):
    model = Location
    template_name = 'inventory/location_uuid_view.html'

class CategoriesView(generic.ListView):
    model = Category
    paginate_by = 25

class LocationView(generic.DetailView):
    model = Location


class CategoryView(generic.DetailView):
    model = Category


class ItemView(generic.DetailView):
    model = Item

def location_uuid_change(request, pk):
    location = get_object_or_404(Location, pk=pk)
    try:
        uuid = UUID(request.POST['uuid'])
    except (KeyError, ValueError):
        return render(request, 'inventory/location_uuid_view.html', {
            'location': location,
            'error_message': "Invalid UUID"
        })
    else:
        location.uuid = uuid
        location.save()
                          
    return HttpResponseRedirect(reverse('inventory:location', args=(location.pk,)))


def location_find_uuid(request, id):
    location = get_object_or_404(Location, uuid=id)
    return render(request, 'inventory/location_detail.html', {'location': location})

def item_new(request, pk):
    location = get_object_or_404(Location, pk=pk)
    if request.method == 'POST':
        form = ItemNewForm(request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('inventory:location', args=(pk,)))

    else:
        item = Item(location=location)
        form = ItemEditForm(instance=item)

    return render(request, 'inventory/item_new.html', {
        'form': form,
        'location': get_object_or_404(Location, pk=pk),
    })

def item_edit(request, pk):
    instance = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemEditForm(request.POST or None, instance=instance)

        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(reverse('inventory:location', args=(instance.location.pk,)))

    else:
        form = ItemEditForm(instance=instance)

    return render(request, 'inventory/item_edit.html', {
        'form': form,
        'instance': instance,
    })

def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    location = item.location
    item.delete()

    return HttpResponseRedirect(reverse('inventory:location', args=(location.pk,)))

def location_delete(request, pk):
    if pk == 1:
        raise Http404("Cannot delete 'Universe'")
    location = get_object_or_404(Location, pk=pk)
    parent = location.parent
    location.delete()

    return HttpResponseRedirect(reverse('inventory:location', args=(parent.pk,)))

def category_delete(request, pk):
    if pk == 1:
        raise Http404("Cannot delete 'Everything'")
    category = get_object_or_404(Category, pk=pk)
    parent = category.parent
    category.delete()

    return HttpResponseRedirect(reverse('inventory:category', args=(parent.pk,)))

def category_edit(request, pk):
    instance = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryEditForm(request.POST, instance=instance)

        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(reverse('inventory:category', args=(instance.pk,)))
    else:
        form = CategoryEditForm(instance=instance)

    return render(request, 'inventory/category_edit.html', {
        'form': form,
        'instance': instance
    })

def category_new(request, pk):
    parent = get_object_or_404(Category, pk=pk)
    instance = Category(parent=parent)
    if request.method == 'POST':
        form = CategoryEditForm(request.POST, instance=instance)

        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(reverse('inventory:category', args=(instance.pk,)))
    else:
        form = CategoryEditForm(instance=instance)

    return render(request, 'inventory/category_new.html', {
        'form': form,
        'instance': instance,
    })

def location_new(request, pk):
    parent = get_object_or_404(Location, pk=pk)
    instance = Location(parent=parent)
    if request.method == 'POST':
        form = LocationEditForm(request.POST, instance=instance)

        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(reverse('inventory:location', args=(instance.pk,)))
    else:
        form = LocationEditForm(instance=instance)

    return render(request, 'inventory/location_new.html', {
        'form': form,
        'instance': instance,
    })

def location_edit(request, pk):
    instance = get_object_or_404(Location, pk=pk)
    if request.method == 'POST':
        form = LocationEditForm(request.POST, instance=instance)

        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(reverse('inventory:location', args=(instance.pk,)))
    else:
        form = LocationEditForm(instance=instance)

    return render(request, 'inventory/location_edit.html', {
        'form': form,
        'instance': instance
    })
