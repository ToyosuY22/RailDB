# Generated by Django 4.1.1 on 2022-10-04 00:17

from django.db import migrations, models
import home.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_alter_user_is_staff'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailToken',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, verbose_name='Eメールアドレス')),
                ('kind', models.CharField(choices=[home.models.EmailToken.KindChoices], max_length=10, verbose_name='種別')),
                ('created_datetime', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('is_used', models.BooleanField(default=False, verbose_name='使用済み')),
            ],
            options={
                'verbose_name': 'Eメールトークン',
                'verbose_name_plural': 'Eメールトークン',
            },
        ),
    ]
