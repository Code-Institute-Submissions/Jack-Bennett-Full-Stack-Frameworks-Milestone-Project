# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-05-25 12:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_tag'),
        ('checkout', '0003_auto_20200525_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='tags',
            field=models.ManyToManyField(to='accounts.Tag'),
        ),
    ]
