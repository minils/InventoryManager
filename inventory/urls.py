from django.urls import include, path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'inventory'
urlpatterns = [
    path('', views.index, name='index'),
    path('locations/', views.LocationsView.as_view(), name='locations'),
    path('location/<int:pk>/', views.LocationView.as_view(), name='location'),
    path('location/<int:pk>/new/', views.location_new, name='locationnew'),
    path('location/<int:pk>/edit/', views.location_edit, name='locationedit'),
    path('location/<int:pk>/trash/', views.location_trash, name='locationtrash'),
    path('location/<int:pk>/untrash/', views.location_untrash, name='locationuntrash'),
    path('location/<int:pk>/delete/', views.location_delete, name='locationdelete'),
    path('location/<int:pk>/uuid/', views.location_edit_uuid, name='locationedituuid'),
    path('location/find/', views.location_find, name='locationfind'),
    path('location/find/<uuid:id>/', views.location_find_uuid, name='locationfinduuid'),
    path('location/<int:pk>/newitem/', views.item_new, name='locationnewitem'),
    path('location/findfreeslot/', views.LocationFindFreeSlot.as_view(), name='locationfindfreeslot'),
    path('categories/', views.CategoriesView.as_view(), name='categories'),
    path('category/<int:pk>/', views.CategoryView.as_view(), name='category'),
    path('category/<int:pk>/new/', views.category_new, name='categorynew'),
    path('category/<int:pk>/edit/', views.category_edit, name='categoryedit'),
    path('category/<int:pk>/trash/', views.category_trash, name='categorytrash'),
    path('category/<int:pk>/untrash/', views.category_untrash, name='categoryuntrash'),
    path('category/<int:pk>/delete/', views.category_delete, name='categorydelete'),
    path('item/<int:pk>/', views.ItemView.as_view(), name='item'),
    path('item/<int:pk>/trash/', views.item_trash, name='itemtrash'),
    path('item/<int:pk>/untrash/', views.item_untrash, name='itemuntrash'),
    path('item/<int:pk>/delete/', views.item_delete, name='itemdelete'),
    path('item/<int:pk>/edit/', views.item_edit, name='itemedit'),
    path('item/<int:pk>/lend/', views.item_lend, name='itemlend'),
    path('item/<int:pk>/returno/)', views.item_return, name='itemreturn'),
    path('search/', views.SearchItem.as_view(), name='search'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/profile', views.AccountsProfile.as_view(), name='profile'),
    #path('accounts/login/', auth_views.LoginView.as_view(template_name='inventory/login.html'), name='login'),
    path('trash/', views.TrashView.as_view(), name='trash'),
]
