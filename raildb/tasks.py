from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from celery import shared_task


def send_email(subject, to, template, context={}):
    """非同期処理でメールを送信

    shared_task つき関数には json-like なデータしか投げられないため、
    この関数で引数を json-like なデータだけにする

    Args:
        subject(str): 件名
        to(str): 送信先メールアドレス
        template(str): 本文テンプレートファイルのパス
        context(dict): 本文テンプレートファイルに流し込む辞書
    """
    # 辞書に要素を追加
    # メールアドレスに該当する User モデルが存在する場合はその表示名を取得
    user_model = get_user_model()

    try:
        to_user = user_model.objects.get(email=to)
        to_name = to_user.display_name
    except user_model.DoesNotExist:
        to_name = None

    context.update({
        'to_name': to_name,
        'settings': settings
    })

    # 本文を作成
    body = render_to_string(template, context)

    # 非同期処理を開始
    send_email_async.delay(subject, to, body)


@shared_task
def send_email_async(subject, to, body):
    """非同期処理でメールを送信

    Args:
        subject(str): 件名
        to(str): 送信先メールアドレス
        body(str): 完成した本文
    """
    email = EmailMessage(
        subject=subject,
        to=[to],
        body=body
    )
    email.send(fail_silently=False)
