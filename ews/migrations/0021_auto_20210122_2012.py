# Generated by Django 3.1.5 on 2021-01-22 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ews', '0020_auto_20210122_1951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='featuredata',
            name='value',
            field=models.DecimalField(decimal_places=1000, max_digits=1000),
        ),
    ]