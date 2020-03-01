# Generated by Django 3.0.2 on 2020-03-01 09:09

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_item_lent_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='state',
            field=models.CharField(choices=[('d', 'default'), ('t', 'trashed'), ('a', 'archived')], default='d', max_length=1),
        ),
        migrations.AlterField(
            model_name='location',
            name='change_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Change date'),
        ),
        migrations.AlterField(
            model_name='location',
            name='creation_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Creation date'),
        ),
        migrations.AlterField(
            model_name='location',
            name='description',
            field=models.CharField(max_length=1000, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='location',
            name='free_space',
            field=models.BooleanField(default=True, verbose_name='Free space'),
        ),
        migrations.AlterField(
            model_name='location',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='location',
            name='parent',
            field=mptt.fields.TreeForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='inventory.Location', verbose_name='Parent'),
        ),
    ]