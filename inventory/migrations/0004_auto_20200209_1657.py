# Generated by Django 3.0.2 on 2020-02-09 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_auto_20200209_1102'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='lent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='item',
            name='lent_to',
            field=models.CharField(default='', max_length=100),
        ),
    ]