from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import gettext as _
from django.contrib.auth.models import User

ITEM_STATES = (
    ('d', 'default'),
    ('t', 'trashed'),
    ('a', 'archived'),
)

class Location(MPTTModel):
    name = models.CharField(verbose_name=_("Name"), max_length=200)
    creation_date = models.DateTimeField(verbose_name=_("Creation date"), default=timezone.now)
    change_date = models.DateTimeField(verbose_name=_("Change date"), auto_now=True)
    parent =  TreeForeignKey('self', on_delete=models.CASCADE, null=True, related_name='children', verbose_name=_("Parent"))
    free_space = models.BooleanField(verbose_name=_("Free space"), default=True)
    uuid = models.UUIDField(verbose_name=_("UUID"), null=True, blank=True)
    description = models.CharField(verbose_name=_("Description"), max_length=1000)
    state = models.CharField(verbose_name=_("State"), max_length=1, choices=ITEM_STATES, default="d")

    def __str__(self):
        return self.name

    class Meta:
        permissions = [
            ('trash_location', 'Can trash location')
        ]

class LocationPrintList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    locations = models.ManyToManyField(Location)

    def for_user(user):
        return LocationPrintList.objects.get(user=user).locations
    

class Category(MPTTModel):
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    creation_date = models.DateTimeField(default=timezone.now, verbose_name=_("Creation Date"))
    change_date = models.DateTimeField(auto_now=True, verbose_name=_("Change Date"))
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, related_name='children', verbose_name=_("Supercategory"))
    description = models.CharField(max_length=1000, verbose_name=_("Description"))
    state = models.CharField(max_length=1, choices=ITEM_STATES, default="d", verbose_name=_("State"))

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = _("Categories")
        permissions = [
            ('trash_category', 'Can trash category')
        ]


class Item(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    creation_date = models.DateTimeField(default=timezone.now, verbose_name=_("Creation Date"))
    change_date = models.DateTimeField(auto_now=True, verbose_name=_("Change Date"))
    location = TreeForeignKey(Location, on_delete=models.CASCADE, null=True, verbose_name=_("Location"))
    amount = models.IntegerField(default=1, validators=[MinValueValidator(0)], verbose_name=_("Amount"))
    description = models.CharField(max_length=1000, verbose_name=_("Description"))
    category = TreeForeignKey(Category, on_delete=models.CASCADE, null=True, verbose_name=_("Category"))
    barcode = models.BigIntegerField(blank=True, null=True, verbose_name=_("Barcode"))
    lent = models.BooleanField(default=False, verbose_name=_("lent"))
    lent_to = models.CharField(max_length=100, default="", verbose_name=_("Lent to"))
    lent_date = models.DateTimeField(null=True, verbose_name=_("Lent Date"))
    state = models.CharField(max_length=1, choices=ITEM_STATES, default="d", verbose_name=_("State"))

    def __str__(self):
        return self.name

    class Meta:
        permissions = [
            ('trash_item', 'Can trash item'),
            ('lend_item', 'Can lend item'),
        ]
    
