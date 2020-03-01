from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import gettext as _

ITEM_STATES = (
    ('d', 'default'),
    ('t', 'trashed'),
    ('a', 'archived'),
)

class Location(MPTTModel):
    name = models.CharField(_("Name"), max_length=200)
    creation_date = models.DateTimeField(_("Creation date"), default=timezone.now)
    change_date = models.DateTimeField(_("Change date"), auto_now=True)
    parent =  TreeForeignKey('self', on_delete=models.CASCADE, null=True, related_name='children', verbose_name=_("Parent"))
    free_space = models.BooleanField(_("Free space"), default=True)
    uuid = models.UUIDField(_("UUID"), null=True, blank=True)
    description = models.CharField(_("Description"), max_length=1000)
    state = models.CharField(max_length=1, choices=ITEM_STATES, default="d")

    def __str__(self):
        return self.name


class Category(MPTTModel):
    name = models.CharField(max_length=200)
    creation_date = models.DateTimeField(default=timezone.now)
    change_date = models.DateTimeField(auto_now=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, related_name='children', verbose_name=_("Supercategory"))
    description = models.CharField(max_length=1000)
    state = models.CharField(max_length=1, choices=ITEM_STATES, default="d")

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = "categories"


class Item(models.Model):
    name = models.CharField(max_length=200)
    creation_date = models.DateTimeField(default=timezone.now)
    change_date = models.DateTimeField(auto_now=True)
    location = TreeForeignKey(Location, on_delete=models.CASCADE, null=True)
    amount = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    description = models.CharField(max_length=1000)
    category = TreeForeignKey(Category, on_delete=models.CASCADE, null=True)
    barcode = models.BigIntegerField(blank=True, null=True)
    lent = models.BooleanField(default=False)
    lent_to = models.CharField(max_length=100, default="", verbose_name=_("Lent to"))
    lent_date = models.DateTimeField(null=True)
    state = models.CharField(max_length=1, choices=ITEM_STATES, default="d")

    def __str__(self):
        return self.name
    
