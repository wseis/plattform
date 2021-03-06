# Generated by Django 3.1.5 on 2021-01-21 16:49

from django.db import migrations, models
import djgeojson.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ews', '0016_auto_20210121_1327'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='location',
            field=djgeojson.fields.PointField(null=True),
        ),
        migrations.AddField(
            model_name='site',
            name='ref_name',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
