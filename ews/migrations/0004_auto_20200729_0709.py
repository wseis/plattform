# Generated by Django 3.0.8 on 2020-07-29 05:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ews', '0003_auto_20200729_0705'),
    ]

    operations = [
        migrations.AlterField(
            model_name='featuredata',
            name='rainstation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data', to='ews.Station'),
        ),
        migrations.AlterField(
            model_name='station',
            name='bathing_spot',
            field=models.ManyToManyField(blank=True, related_name='stations', to='ews.BathingSpot'),
        ),
    ]
