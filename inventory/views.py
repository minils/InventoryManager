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
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin

from uuid import UUID

from .models import Item, Location, Category, LocationPrintList
from .forms import LocationEditForm, ItemEditForm, ItemLendForm, CategoryEditForm, LocationUuidEditForm

logger = logging.getLogger(__name__)

types = ['item', 'category', 'location']

@permission_required('inventory.view_item')
@permission_required('inventory.view_location')
@permission_required('inventory.view_category')
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

class SearchItem(PermissionRequiredMixin, generic.ListView):
    permission_required = ('inventory.view_item', 'inventory.view_location','inventory.view_category')
    paginate_by = 25
    template_name = 'inventory/search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_term'] = self.request.GET['q']
        if self.request.GET['type'] in types:
            context['search_type'] = self.request.GET['type']
        else:
            context['search_type'] = types[0]
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

class LocationsView(PermissionRequiredMixin, generic.ListView):
    permission_required = ('inventory.view_location')
    model = Location
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Locations")
        return context

    def get_queryset(self):
        return Location.objects.filter(state__exact='d')
    

class CategoriesView(PermissionRequiredMixin, generic.ListView):
    permission_required = ('inventory.view_category')
    model = Category
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Categories")
        return context

class LocationView(PermissionRequiredMixin, generic.ListView):
    permission_required = ('inventory.view_item', 'inventory.view_location','inventory.view_category')
    model = Item
    template_name = 'inventory/location_detail.html'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        location = Location.objects.get(pk=kwargs['pk'])
        self.object_list = Item.objects.filter(location__exact=location, state__exact='d').order_by('name')

        context = self.get_context_data()
        context['location'] = location
        context['location_list'] = location.get_descendants().filter(state__exact='d')
        context['title'] = _("Location")
        return self.render_to_response(context)

    
class CategoryView(PermissionRequiredMixin, generic.ListView):
    permission_required = ('inventory.view_item', 'inventory.view_location', 'inventory.view_category')
    model = Item
    template_name = 'inventory/category_detail.html'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        category = Category.objects.get(pk=kwargs['pk'])
        self.object_list = Item.objects.filter(category__exact=category, state__exact='d')

        context = self.get_context_data()
        context['category'] = category
        context['subcategories'] = category.get_descendants().filter(state__exact='d')
        context['title'] = _("Category")
        return self.render_to_response(context)


class ItemView(PermissionRequiredMixin, generic.DetailView):
    permission_required = ('inventory.view_item')
    model = Item

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Item")
        return context

@permission_required('inventory.edit_location')
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

@permission_required('inventory.view_location')
def location_find(request):
    if 'uuid' in request.GET:
        uuid = request.GET['uuid']
        return HttpResponseRedirect(reverse('inventory:locationfinduuid', args=(uuid,)))
    
    return render(request, 'inventory/location_find.html', {
    })


class LocationFindFreeSlot(PermissionRequiredMixin, generic.ListView):
    permission_required = ('inventory.view_item', 'inventory.view_location', 'inventory.view_category')
    model = Location
    paginate_by = 25
    template_name = 'inventory/location_findfreeslot.html'

    def get_queryset(self):
        locations = Location.objects.filter(free_space__exact=True)
        return locations

@permission_required('inventory.view_location')
def location_find_uuid(request, id):
    location = get_object_or_404(Location, uuid=id)
    return render(request, 'inventory/location_detail.html', {
        'title': _("Find location"),
        'location': location,
    })

@permission_required('inventory.view_location')
@permission_required('inventory.view_category')
@permission_required('inventory.add_item')
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

@permission_required('inventory.view_item')
@permission_required('inventory.view_item')
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

@permission_required('inventory.delete_item')
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if item.state != 't':
        raise Http404("Item must be trashed first.")
    item.delete()

    return HttpResponseRedirect(reverse('inventory:trash'))

@permission_required('inventory.trash_item')
def item_trash(request, pk):
    item = get_object_or_404(Item, pk=pk)
    location = item.location
    item.state = 't'
    item.save()

    return HttpResponseRedirect(reverse('inventory:location', args=(location.pk,)))

@permission_required('inventory.trash_item')
def item_untrash(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if item.state != 't':
        raise Http404(_("Cannot untrash non-trashed item"))
    item.state = 'd'
    item.save()

    return HttpResponseRedirect(reverse('inventory:trash', args=()))
    
@permission_required('inventory.lend_item')
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

def redirect_next(request, item, message):
    if 'next' in request:
        raise Http404(_("Missing argument"))
    if request.GET['next'] not in types:
        raise Http404(_("Wrong 'next' argument"))
    if 'next' == 'item':
        return HttpResponseRedirect(reverse('inventory:item', args=(item.pk,)))

@permission_required('inventory.lend_item')
def item_return(request, pk):
    instance = get_object_or_404(Item, pk=pk)
    if instance.lent == False:
        return HttpResponseRedirect(reverse('inventory:item', args=(item.pk,)))
        #redirect_next(request, pk, "")
    else:
        instance.lent = False
        instance.lent_to = ""
        instance.lent_date = timezone.now()
        instance.save()
        return HttpResponseRedirect(reverse('inventory:item', args=(instance.pk,)))

@permission_required('inventory.delete_location')
def location_delete(request, pk):
    location = get_object_or_404(Location, pk=pk)
    if location.state != 't':
        raise Http404("Location must be trashed first.")
    location.delete()
    return HttpResponseRedirect(reverse('inventory:trash'))

@permission_required('inventory.trash_location')
def location_trash(request, pk):
    if pk == 1:
        raise Http404(_("Cannot trash 'Universe'"))
    location = get_object_or_404(Location, pk=pk)
    if location.children.count() != 0:
        error_message = _("Cannot trash location with sublocations.")
        return render(request, 'inventory/location_detail.html', {
            'title': _("Trash location"),
            'error_message': error_message,
            'location': location,
        })
    elif location.item_set.count() != 0:
        error_message = _("Cannot trash non-empty location.")
        return render(request, 'inventory/location_detail.html', {
            'title': _("Trash location"),
            'error_message': error_message,
            'location': location,
        })

    parent = location.parent
    location.state = 't'
    location.save()

    return HttpResponseRedirect(reverse('inventory:location', args=(parent.pk,)))

@permission_required('inventory.trash_location')
def location_untrash(request, pk):
    location = get_object_or_404(Location, pk=pk)
    if location.state != 't':
        raise Http404(_("Cannot untrash non-trashed location"))
    location.state = 'd'
    location.save()

    return HttpResponseRedirect(reverse('inventory:trash', args=()))

@permission_required('inventory.delete_category')
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if category.state != 't':
        raise Http404("Category must be trashed first.")
    category.delete()
    return HttpResponseRedirect(reverse('inventory:trash'))

@permission_required('inventory.trash_category')
def category_trash(request, pk):
    if pk == 1:
        raise Http404(_("Cannot trash 'Everything'"))
    category = get_object_or_404(Category, pk=pk)
    if category.children.count() != 0:
        error_message = _("Cannot be trashd because subcategories exist.")
        return render(request, 'inventory/category_detail.html', {
            'title': _("Trash category"),
            'error_message': error_message,
            'category': category,
        })
    parent = category.parent
    category.state = 't'
    category.save()

    return HttpResponseRedirect(reverse('inventory:category', args=(parent.pk,)))

@permission_required('inventory.trash_category')
def category_untrash(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if category.state != 't':
        raise Http404(_("Cannot untrash non-trashed category"))
    category.state = 'd'
    category.save()

    return HttpResponseRedirect(reverse('inventory:trash', args=()))

@permission_required('inventory.edit_category')
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

@permission_required('inventory.add_category')
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

@permission_required('inventory.add_location')
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

@permission_required('inventory.add_location')
def location_new_multiple(request, pk):
    logger.warn("Yesssss")
    parent = get_object_or_404(Location, pk=pk)
    instance = Location(parent=parent)
    if request.method == 'POST':
        form = LocationEditForm(request.POST, instance=instance)

        if form.is_valid() and 'amount' in request.POST:
            # Create 'amount' locations and name them 'Name 1', 'Name 2', etc
            try:
                amount = int(request.POST['amount'])
                for i in range(amount):
                    l = Location.objects.create(name="{} {}".format(form.cleaned_data['name'], i+1),
                                                description="{} {}".format(form.cleaned_data['description'], i+1),
                                                parent=parent)
                
                return HttpResponseRedirect(reverse('inventory:location', args=(pk,)))
            except:
                return HttpResponseRedirect(reverse('inventory:location', args=(pk,)))
    else:
        form = LocationEditForm(instance=instance)

    return render(request, 'inventory/location_new_multiple.html', {
        'form': form,
        'instance': instance,
    })

@permission_required('inventory.edit_location')
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


@permission_required('inventory.view_location')
def print_list(request):
    try:
        print_list = LocationPrintList.objects.get(user=request.user)
    except:
        print_list = LocationPrintList.objects.create(user=request.user) 
    return render(request, 'inventory/print_list.html', {
        'list': print_list.locations.all().order_by('name')
    })

@permission_required('inventory.view_location')
def print_list_clear(request):
    try:
        print_list = LocationPrintList.objects.get(user=request.user)
        print_list.locations.clear()
        return HttpResponseRedirect(reverse('inventory:print_list'))
    except:
        return HttpResponseRedirect(reverse('inventory:print_list'))

@permission_required('inventory.view_location')
def print_list_add(request, pk):
    try:
        print_list = LocationPrintList.for_user(user=request.user)
        l = get_object_or_404(Location, pk=pk)
        print_list.add(l)
        return HttpResponseRedirect(reverse('inventory:print_list'))
    except:
        return HttpResponseRedirect(reverse('inventory:print_list'))
    
@permission_required('inventory.view_location')
def print_list_remove(request, pk):
    try:
        print_list = LocationPrintList.for_user(user=request.user)
        l = get_object_or_404(Location, pk=pk)
        print_list.remove(l)
        return HttpResponseRedirect(reverse('inventory:print_list'))
    except:
        return HttpResponseRedirect(reverse('inventory:print_list'))


class AccountsProfile(LoginRequiredMixin, generic.DetailView):
    model = User
    template_name = 'inventory/user_detail.html'

    def get_object(self):
        return self.request.user


class TrashView(PermissionRequiredMixin, generic.ListView):
    permission_required = ('inventory.view_item', 'inventory.view_location', 'inventory.view_category')
    paginate_by = 25
    template_name = 'inventory/trash.html'

    def get(self, request, *args, **kwargs):
        if 'type' in self.request.GET and self.request.GET['type'] in types:
            search_type = self.request.GET['type']
        else:
            search_type = types[0]

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

    
