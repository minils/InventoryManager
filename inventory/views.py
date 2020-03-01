import logging
from django.utils.datastructures import MultiValueDictKeyError
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext as _

from uuid import UUID

from .models import Item, Location, Category
from .forms import LocationEditForm, ItemEditForm, ItemLendForm, CategoryEditForm, LocationUuidEditForm

logger = logging.getLogger(__name__)

def index(request):
    latest_items = Item.objects.order_by('-creation_date')[:5]
    categories = Category.objects.order_by('-creation_date')[:5]
    locations = Location.objects.order_by('-creation_date')[:5]
    return render(request, 'inventory/index.html', {
        'title': 'Home',
        'latest_items': latest_items,
        'categories': categories,
        'locations': locations,
        'nav_item': _("Home"),
    })

class SearchItem(generic.ListView):
    paginate_by = 25
    template_name = 'inventory/search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_term'] = self.request.GET['q']
        if self.request.GET['type'] in search_types:
            context['search_type'] = self.request.GET['type']
        else:
            context['search_type'] = search_types[0]
        if len(context['search_term']) < 3:
            context['error_message'] = _("Search term must contain at least 3 letters.")
        context['title'] = _("Search")
        return context
    
    def get_queryset(self):
        search_term = self.request.GET['q']
        search_type = self.request.GET['type']
        if len(search_term) < 3:
            return []
        else:
            if search_type == 'item':
                results = Item.objects.filter(name__icontains=search_term).order_by('name')
            elif search_type == 'location':
                results = Location.objects.filter(name__icontains=search_term).order_by('name')
            elif search_type == 'category':
                results = Category.objects.filter(name__icontains=search_term).order_by('name')
            else:
                results = []
            return results

class LocationsView(generic.ListView):
    model = Location
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Locations")
        return context
    

class CategoriesView(generic.ListView):
    model = Category
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Categories")
        return context

class LocationView(generic.ListView):
    model = Item
    template_name = 'inventory/location_detail.html'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        location = Location.objects.get(pk=kwargs['pk'])
        self.object_list = Item.objects.filter(location__exact=location, state__exact='d')

        context = self.get_context_data()
        context['location'] = location
        context['title'] = _("Location")
        return self.render_to_response(context)

    
class CategoryView(generic.ListView):
    model = Item
    template_name = 'inventory/category_detail.html'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        category = Category.objects.get(pk=kwargs['pk'])
        self.object_list = Item.objects.filter(category__exact=category, state__exact='d')

        context = self.get_context_data()
        context['category'] = category
        context['title'] = _("Category")
        return self.render_to_response(context)


class ItemView(generic.DetailView):
    model = Item

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Item")
        return context

def location_edit_uuid(request, pk):
    location = get_object_or_404(Location, pk=pk)
    if request.method == 'POST':
        form = LocationUuidEditForm(request.POST, instance=location)
        
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('inventory:location', args=(location.pk,)))
    else:
        form = LocationUuidEditForm(instance=location)

    return render(request, 'inventory/location_edit_uuid.html', {
        'title': _("Edit Location"),
        'form': form,
        'location': location,
    })

def location_find(request):
    if 'uuid' in request.GET:
        uuid = request.GET['uuid']
        return HttpResponseRedirect(reverse('inventory:locationfinduuid', args=(uuid,)))
    
    return render(request, 'inventory/location_find.html', {
    })


class LocationFindFreeSlot(generic.ListView):
    model = Location
    paginate_by = 25
    template_name = 'inventory/location_findfreeslot.html'

    def get_queryset(self):
        locations = Location.objects.filter(free_space__exact=True)
        return locations

def location_find_uuid(request, id):
    location = get_object_or_404(Location, uuid=id)
    return render(request, 'inventory/location_detail.html', {
        'title': _("Find location"),
        'location': location,
    })

def item_new(request, pk):
    location = get_object_or_404(Location, pk=pk)
    category = Category.objects.get(pk=1)
    if request.method == 'POST':
        form = ItemEditForm(request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('inventory:location', args=(pk,)))

    else:
        item = Item(location=location, category=category)
        form = ItemEditForm(instance=item)

    return render(request, 'inventory/item_new.html', {
        'title': _("New item"),
        'form': form,
        'location': location,
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
        'title': _("Edit item"),
        'form': form,
        'instance': instance,
    })

def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    location = item.location
    item.state = 't'
    item.save()

    return HttpResponseRedirect(reverse('inventory:location', args=(location.pk,)))

def item_undelete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if item.state != 't':
        raise Http404(_("Cannot undelete non-trashed item"))
    item.state = 'd'
    item.save()

    return HttpResponseRedirect(reverse('inventory:trash', args=()))
    

def item_lend(request, pk):
    instance = get_object_or_404(Item, pk=pk)

    if request.method == 'POST':
        form = ItemLendForm(request.POST or None, instance=instance)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.lent = True
            instance.lent_date = timezone.now()
            instance.save()
            return HttpResponseRedirect(reverse('inventory:item', args=(instance.pk,)))

    else:
        form = ItemLendForm(instance=instance)

    return render(request, 'inventory/item_lend.html', {
        'title': _("Lend item"),
        'form': form,
        'instance': instance,
    })

def item_return(request, pk):
    instance = get_object_or_404(Item, pk=pk)
    if instance.lent == False:
        return HttpResponseRedirect(reverse('inventory:item', args=(instance.pk,)))
    else:
        instance.lent = False
        instance.lent_to = ""
        instance.lent_date = timezone.now()
        instance.save()
        return HttpResponseRedirect(reverse('inventory:item', args=(instance.pk,)))

def location_delete(request, pk):
    if pk == 1:
        raise Http404(_("Cannot delete 'Universe'"))
    location = get_object_or_404(Location, pk=pk)
    if location.children.count() != 0:
        error_message = _("Cannot be deleted because sublocations exist.")
        return render(request, 'inventory/location_detail.html', {
            'title': _("Delete item"),
            'error_message': error_message,
            'location': location,
        })
    parent = location.parent
    location.state = 't'
    location.save()

    return HttpResponseRedirect(reverse('inventory:location', args=(parent.pk,)))

def location_undelete(request, pk):
    location = get_object_or_404(Location, pk=pk)
    if location.state != 't':
        raise Http404(_("Cannot undelete non-trashed location"))
    location.state = 'd'
    location.save()

    return HttpResponseRedirect(reverse('inventory:trash', args=()))

def category_delete(request, pk):
    if pk == 1:
        raise Http404(_("Cannot delete 'Everything'"))
    category = get_object_or_404(Category, pk=pk)
    if category.children.count() != 0:
        error_message = _("Cannot be deleted because subcategories exist.")
        return render(request, 'inventory/category_detail.html', {
            'title': _("Delete category"),
            'error_message': error_message,
            'category': category,
        })
    parent = category.parent
    category.state = 't'
    category.save()

    return HttpResponseRedirect(reverse('inventory:category', args=(parent.pk,)))

def category_undelete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if category.state != 't':
        raise Http404(_("Cannot undelete non-trashed category"))
    category.state = 'd'
    category.save()

    return HttpResponseRedirect(reverse('inventory:trash', args=()))

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

class AccountsProfile(generic.DetailView):
    model = User
    template_name = 'inventory/user_detail.html'

    def get_object(self):
        return self.request.user

search_types = ['item', 'category', 'location']
class TrashView(generic.ListView):
    paginate_by = 25
    template_name = 'inventory/trash.html'

    def get(self, request, *args, **kwargs):
        if 'type' in self.request.GET and self.request.GET['type'] in search_types:
            search_type = self.request.GET['type']
        else:
            search_type = search_types[0]

        if search_type == 'item':
            self.object_list = Item.objects.filter(state__exact='t')
        elif search_type == 'location':
            self.object_list = Location.objects.filter(state__exact='t')
        elif search_type == 'category':
            self.object_list = Category.objects.filter(state__exact='t')
            
        context = self.get_context_data()
        context['search_type'] = search_type
        context['title'] = _("Trash")

        return self.render_to_response(context) 

    
