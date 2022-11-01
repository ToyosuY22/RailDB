# Generated by Django 4.1.2 on 2022-10-26 14:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0005_alter_railway_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='line',
            name='operator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='library.operator', verbose_name='事業者'),
        ),
        migrations.AlterField(
            model_name='station',
            name='line',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='library.line', verbose_name='路線'),
        ),
    ]