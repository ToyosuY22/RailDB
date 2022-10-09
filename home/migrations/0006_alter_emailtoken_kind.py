# Generated by Django 4.1.2 on 2022-10-07 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_alter_user_display_name_alter_user_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailtoken',
            name='kind',
            field=models.CharField(choices=[('signup', 'アカウント新規登録'), ('pwreset', 'パスワード再設定'), ('emailupd', 'Eメールアドレス変更')], max_length=10, verbose_name='種別'),
        ),
    ]