# Generated by Django 4.0.6 on 2024-08-06 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rtdf', '0041_alter_medicamento_total_mg'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pacientereceta',
            name='timestamp',
            field=models.DateTimeField(),
        ),
    ]
