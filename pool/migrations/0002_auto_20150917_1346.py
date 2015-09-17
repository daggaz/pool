# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ranking',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mu', models.FloatField(null=True)),
                ('sigma', models.FloatField(null=True)),
            ],
            options={
                'ordering': ('game__created',),
            },
        ),
        migrations.AlterModelOptions(
            name='game',
            options={'ordering': ('created',)},
        ),
        migrations.AddField(
            model_name='ranking',
            name='game',
            field=models.ForeignKey(related_name='rankings', to='pool.Game'),
        ),
        migrations.AddField(
            model_name='ranking',
            name='player',
            field=models.ForeignKey(related_name='rankings', to='pool.Player'),
        ),
    ]
