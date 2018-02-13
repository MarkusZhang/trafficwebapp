# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bounds',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('north', models.FloatField()),
                ('south', models.FloatField()),
                ('east', models.FloatField()),
                ('west', models.FloatField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Heatmap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('recorded_time', models.DateTimeField(null=True)),
                ('raw_data', models.TextField(null=True, blank=True)),
                ('json_data', models.TextField(null=True, blank=True)),
                ('note', models.CharField(unique=True, max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('recorded_time', models.DateTimeField()),
                ('num_points', models.IntegerField(default=0)),
                ('note', models.CharField(unique=True, max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MessageLevel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('disp_level', models.IntegerField()),
                ('category', models.CharField(max_length=2, choices=[(b'A', b'A'), (b'B', b'B'), (b'C', b'C')])),
                ('message', models.ForeignKey(to='webapp.Message')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MessageLevelPiece',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('p_x', models.IntegerField(default=0)),
                ('p_y', models.IntegerField(default=0)),
                ('num_points', models.IntegerField(default=0)),
                ('point_size', models.IntegerField(default=20)),
                ('raw_data', models.TextField()),
                ('json_data', models.TextField(null=True, blank=True)),
                ('bounds', models.OneToOneField(null=True, to='webapp.Bounds')),
                ('message_level', models.ForeignKey(to='webapp.MessageLevel')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RoadNetwork',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('x_grid', models.IntegerField(default=10)),
                ('y_grid', models.IntegerField(default=10)),
                ('name', models.CharField(max_length=200)),
                ('bounds', models.OneToOneField(to='webapp.Bounds')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RoadSeg',
            fields=[
                ('id', models.CharField(max_length=200, serialize=False, primary_key=True)),
                ('category', models.CharField(max_length=200, choices=[[b'A', b'A'], [b'B', b'B'], [b'C', b'C'], [b'D', b'D'], [b'E', b'E'], [b'N', b'N'], [b'S', b'S']])),
                ('name', models.CharField(max_length=500)),
                ('start_lng', models.FloatField()),
                ('start_lat', models.FloatField()),
                ('end_lng', models.FloatField()),
                ('end_lat', models.FloatField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RoadSegGrid',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
                ('road_network', models.ForeignKey(to='webapp.RoadNetwork')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Traffic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('recorded_time', models.DateTimeField(null=True)),
                ('note', models.CharField(unique=True, max_length=50)),
                ('speed_records', models.TextField(default=b'')),
                ('type', models.CharField(default=b'history', max_length=50, choices=[(b'typical', b'typical'), (b'history', b'history')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrafficeLayerPiece',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('num_records', models.IntegerField(null=True)),
                ('piece_num', models.IntegerField()),
                ('p_x', models.IntegerField(default=0)),
                ('p_y', models.IntegerField(default=0)),
                ('raw_data', models.TextField()),
                ('raw_data_cutoff', models.CharField(max_length=200)),
                ('json_data', models.TextField()),
                ('bounds', models.OneToOneField(null=True, to='webapp.Bounds')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrafficLayer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('disp_level', models.IntegerField()),
                ('category', models.CharField(max_length=5, choices=[(b'A', b'A'), (b'B', b'B'), (b'C', b'C'), (b'D', b'D'), (b'E', b'E'), (b'S', b'S'), (b'N', b'N')])),
                ('traffic', models.ForeignKey(to='webapp.Traffic')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='trafficelayerpiece',
            name='traffic_layer',
            field=models.ForeignKey(to='webapp.TrafficLayer'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='roadseg',
            name='road_seg_grid',
            field=models.ManyToManyField(to='webapp.RoadSegGrid'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='messagelevel',
            unique_together=set([('category', 'message')]),
        ),
    ]
