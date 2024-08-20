# Generated by Django 4.0.6 on 2024-08-19 16:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rtdf', '0053_alter_pacientereceta_estado'),
    ]

    operations = [
        migrations.CreateModel(
            name='AudioscoefIngesta',
            fields=[
                ('id_audiocoeficientes', models.AutoField(primary_key=True, serialize=False)),
                ('paciente', models.CharField(max_length=100)),
                ('genero', models.CharField(max_length=1)),
                ('nombre_archivo', models.CharField(max_length=100)),
                ('fecha_coeficiente', models.DateTimeField()),
                ('fecha_audio', models.DateField()),
                ('dosis_ingesta', models.DecimalField(decimal_places=2, max_digits=5)),
                ('dt_ingesta', models.IntegerField()),
                ('f0', models.CharField(max_length=100)),
                ('f1', models.CharField(max_length=100)),
                ('f2', models.CharField(max_length=100)),
                ('f3', models.CharField(max_length=100)),
                ('f4', models.CharField(max_length=100)),
                ('intensidad', models.CharField(max_length=100)),
                ('hnr', models.CharField(max_length=100)),
                ('local_jitter', models.CharField(max_length=100)),
                ('local_absolute_jitter', models.CharField(max_length=100)),
                ('rap_jitter', models.CharField(max_length=100)),
                ('ppq5_jitter', models.CharField(max_length=100)),
                ('ddp_jitter', models.CharField(max_length=100)),
                ('local_shimmer', models.CharField(max_length=100)),
                ('local_db_shimmer', models.CharField(max_length=100)),
                ('apq3_shimmer', models.CharField(max_length=100)),
                ('aqpq5_shimmer', models.CharField(max_length=100)),
                ('apq11_shimmer', models.CharField(max_length=100)),
                ('id_audio', models.ForeignKey(db_column='id_audio', on_delete=django.db.models.deletion.CASCADE, to='rtdf.pacienteaudioingesta')),
            ],
            options={
                'verbose_name_plural': 'audiocoeficiente ingesta',
                'db_table': 'audioscoeficientes_ingesta',
            },
        ),
    ]
