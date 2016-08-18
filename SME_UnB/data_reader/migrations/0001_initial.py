# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CommunicationProtocol',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('protocol_type', models.CharField(max_length=50)),
                ('port', models.IntegerField(default=1001)),
                ('timeout', models.FloatField(default=30.0)),
            ],
        ),
        migrations.CreateModel(
            name='EnergyMeasurements',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('collection_date', models.DateTimeField(verbose_name='date published')),
                ('voltage_a', models.FloatField(default=None)),
                ('voltage_b', models.FloatField(default=None)),
                ('voltage_c', models.FloatField(default=None)),
                ('current_a', models.FloatField(default=None)),
                ('current_b', models.FloatField(default=None)),
                ('current_c', models.FloatField(default=None)),
                ('active_power_a', models.FloatField(default=None)),
                ('active_power_b', models.FloatField(default=None)),
                ('active_power_c', models.FloatField(default=None)),
                ('reactive_power_a', models.FloatField(default=None)),
                ('reactive_power_b', models.FloatField(default=None)),
                ('reactive_power_c', models.FloatField(default=None)),
                ('apparent_power_a', models.FloatField(default=None)),
                ('apparent_power_b', models.FloatField(default=None)),
                ('apparent_power_c', models.FloatField(default=None)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EnergyTransductor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('serie_number', models.IntegerField(default=None)),
                ('ip_address', models.CharField(unique=True, max_length=15)),
                ('description', models.TextField(max_length=150)),
                ('creation_date', models.DateTimeField(verbose_name='date published')),
                ('data_collection', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='energymeasurements',
            name='transductor',
            field=models.ForeignKey(to='data_reader.EnergyTransductor'),
        ),
        migrations.AddField(
            model_name='communicationprotocol',
            name='transductor',
            field=models.ForeignKey(to='data_reader.EnergyTransductor'),
        ),
    ]
