# Generated by Django 4.1.7 on 2023-08-10 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tool', '0029_auto_20230529_1247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]