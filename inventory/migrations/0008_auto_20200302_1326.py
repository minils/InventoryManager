# Generated by Django 3.0.2 on 2020-03-02 13:26

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_auto_20200301_0910'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'permissions': [('trash_category', 'Can trash category')], 'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterModelOptions(
            name='item',
            options={'permissions': [('trash_item', 'Can trash item'), ('leden_item', 'Can lend item')]},
        ),
        migrations.AlterModelOptions(
            name='location',
            options={'permissions': [('trash_location', 'Can trash location')]},
        ),
        migrations.AlterField(
            model_name='category',
            name='change_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Change Date'),
        ),
        migrations.AlterField(
            model_name='category',
            name='creation_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Creation Date'),
        ),
        migrations.AlterField(
            model_name='category',
            name='description',
            field=models.CharField(max_length=1000, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='category',
            name='state',
            field=models.CharField(choices=[('d', 'default'), ('t', 'trashed'), ('a', 'archived')], default='d', max_length=1, verbose_name='State'),
        ),
        migrations.AlterField(
            model_name='item',
            name='amount',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Amount'),
        ),
        migrations.AlterField(
            model_name='item',
            name='barcode',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='Barcode'),
        ),
        migrations.AlterField(
            model_name='item',
            name='category',
            field=mptt.fields.TreeForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.Category', verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='item',
            name='change_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Change Date'),
        ),
        migrations.AlterField(
            model_name='item',
            name='creation_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Creation Date'),
        ),
        migrations.AlterField(
            model_name='item',
            name='description',
            field=models.CharField(max_length=1000, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='item',
            name='lent',
            field=models.BooleanField(default=False, verbose_name='lent'),
        ),
        migrations.AlterField(
            model_name='item',
            name='lent_date',
            field=models.DateTimeField(null=True, verbose_name='Lent Date'),
        ),
        migrations.AlterField(
            model_name='item',
            name='lent_to',
            field=models.CharField(default='', max_length=100, verbose_name='Lent to'),
        ),
        migrations.AlterField(
            model_name='item',
            name='location',
            field=mptt.fields.TreeForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.Location', verbose_name='Location'),
        ),
        migrations.AlterField(
            model_name='item',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='item',
            name='state',
            field=models.CharField(choices=[('d', 'default'), ('t', 'trashed'), ('a', 'archived')], default='d', max_length=1, verbose_name='State'),
        ),
        migrations.AlterField(
            model_name='location',
            name='state',
            field=models.CharField(choices=[('d', 'default'), ('t', 'trashed'), ('a', 'archived')], default='d', max_length=1, verbose_name='State'),
        ),
    ]
