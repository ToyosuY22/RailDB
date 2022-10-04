# Generated by Django 4.1.2 on 2022-10-04 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_emailtoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='display_name',
            field=models.CharField(help_text='そらちゃん', max_length=50, verbose_name='表示名'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(help_text='tokino_sora@hololive.com', max_length=254, unique=True, verbose_name='Eメールアドレス'),
        ),
    ]
