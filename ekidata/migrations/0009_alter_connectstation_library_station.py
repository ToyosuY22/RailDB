# Generated by Django 4.2.2 on 2023-06-29 13:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0005_alter_station_freight'),
        ('ekidata', '0008_connectstation_delete_connectstationgroup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connectstation',
            name='library_station',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='library.station', verbose_name='ライブラリ_駅'),
        ),
    ]
