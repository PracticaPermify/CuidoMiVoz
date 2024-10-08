# Generated by Django 4.0.6 on 2024-08-16 16:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rtdf', '0051_remove_pacienteingesta_fecha_ingesta_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pacienteingesta',
            name='recordatorio_1',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pacienteingesta',
            name='recordatorio_2',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pacienteingesta',
            name='recordatorio_3',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pacientereceta',
            name='estado',
            field=models.CharField(default=1, max_length=1),
        ),
        migrations.CreateModel(
            name='PacienteAudioIngesta',
            fields=[
                ('id_audio_ingesta', models.AutoField(primary_key=True, serialize=False)),
                ('url_audio', models.CharField(max_length=200)),
                ('fecha_audio', models.DateTimeField()),
                ('fk_paciente', models.ForeignKey(db_column='fk_paciente', on_delete=django.db.models.deletion.CASCADE, to='rtdf.paciente')),
            ],
            options={
                'verbose_name_plural': 'audios paciente ingesta',
                'db_table': 'paciente_audio_ingesta',
            },
        ),
    ]
