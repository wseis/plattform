# Generated by Django 3.0.8 on 2020-07-29 08:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ews', '0005_auto_20200729_0713'),
    ]

    operations = [
        migrations.RenameField(
            model_name='station',
            old_name='PredictorType',
            new_name='feature_type',
        ),
    ]
