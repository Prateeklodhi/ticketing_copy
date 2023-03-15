# Generated by Django 3.2.10 on 2023-02-08 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tool', '0015_alter_nidanticket_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nidanticket',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('solved', 'solved')], default='pending', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='priority',
            field=models.IntegerField(blank=3, choices=[(1, 'Critical'), (2, 'High'), (3, 'Normal'), (4, 'Low'), (5, 'Very Low')], default=3),
        ),
    ]
