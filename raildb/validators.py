from django.core.validators import RegexValidator


class KanaRegexValidator(RegexValidator):
    """かな専用バリデーター
    """
    regex = r'[ぁ-んー]+'
    message = 'ひらがなで入力してください！'
