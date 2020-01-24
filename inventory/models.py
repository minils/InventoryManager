from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from mptt.models import MPTTModel, TreeForeignKey

class Location(MPTTModel):
    name = models.CharField(max_length=200)
    creation_date = models.DateTimeField(default=timezone.now)
    change_date = models.DateTimeField(auto_now=True)
    parent =  TreeForeignKey('self', on_delete=models.CASCADE, null=True, related_name='children')
    free_space = models.BooleanField(default=True)
    uuid = models.UUIDField(null=True, blank=True)
    description = models.CharField(max_length=1000)

    def __str__(self):
        return self.name


class Category(MPTTModel):
    name = models.CharField(max_length=200)
    creation_date = models.DateTimeField(default=timezone.now)
    change_date = models.DateTimeField(auto_now=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, related_name='children', verbose_name='Supercategory')
    description = models.CharField(max_length=1000)

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
    barcode = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name
    
