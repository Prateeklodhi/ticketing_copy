# Generated by Django 3.2.10 on 2023-02-06 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tool', '0014_alter_nidanticket_docket_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nidanticket',
            name='status',
            field=models.CharField(choices=[('Panding', 'Panding'), ('Solved', 'Solved')], default='Panding', max_length=100, null=True),
        ),
    ]