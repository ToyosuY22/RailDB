# Generated by Django 4.2.2 on 2023-06-25 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0004_linerelationship'),
    ]

    operations = [
        migrations.AlterField(
            model_name='station',
            name='freight',
            field=models.CharField(blank=True, choices=[('freight', '貨物駅'), ('ors', 'オフレールステーション'), ('office', '新営業所')], max_length=20, null=True, verbose_name='貨物情報'),
        ),
    ]
