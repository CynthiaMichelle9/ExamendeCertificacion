# Generated by Django 4.2.3 on 2023-07-11 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('principal', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='direcciondespacho',
            name='region',
            field=models.CharField(max_length=80),
        ),
    ]
