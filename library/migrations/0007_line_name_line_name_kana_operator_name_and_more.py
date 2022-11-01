# Generated by Django 4.1.2 on 2022-10-27 14:50

from django.db import migrations, models
import raildb.validators


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0006_alter_line_operator_alter_station_line'),
    ]

    operations = [
        migrations.AddField(
            model_name='line',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='名称'),
        ),
        migrations.AddField(
            model_name='line',
            name='name_kana',
            field=models.CharField(blank=True, max_length=100, null=True, validators=[raildb.validators.KanaRegexValidator], verbose_name='名称かな'),
        ),
        migrations.AddField(
            model_name='operator',
            name='name',
            field=models.CharField(default='hoge', max_length=100, verbose_name='名称'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='operator',
            name='name_kana',
            field=models.CharField(default='hoge', max_length=100, validators=[raildb.validators.KanaRegexValidator], verbose_name='名称かな'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='station',
            name='name',
            field=models.CharField(default='hoge', max_length=100, verbose_name='名称'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='station',
            name='name_kana',
            field=models.CharField(default='hoge', max_length=100, validators=[raildb.validators.KanaRegexValidator], verbose_name='名称かな'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Railway',
        ),
    ]
