from django.contrib import admin

from mptt.admin import MPTTModelAdmin
from .models import Location, Item, Category

class ItemAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'amount', 'location', 'category']
    list_display = ['name','amount',  'description', 'category', 'location', 'creation_date']
    list_filter = ['category', 'location']
    search_fields = ['name', 'description']

class LocationAdmin(MPTTModelAdmin):
    fields = ['name', 'description', 'free_space', 'parent', 'uuid']
    list_display = ['name', 'description', 'creation_date']
    list_filter = ['creation_date']
    search_fields = ['name', 'description']

class CategoryAdmin(MPTTModelAdmin):
    fields = ['name', 'description', 'parent']
    list_display = ['name', 'description', 'creation_date']
    list_filter = ['creation_date']
    search_fields = ['name', 'description']
    
admin.site.register(Item, ItemAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Category, CategoryAdmin)
