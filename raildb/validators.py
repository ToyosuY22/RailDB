from django.core.validators import RegexValidator


class KanaRegexValidator(RegexValidator):
    """かな専用バリデーター
    """
    regex = r'[ぁ-んー]+'
    message = 'ひらがなで入力してください！'


class KatakanaRegexValidator(RegexValidator):
    """カナ専用バリデーター
    """
    regex = r'[ァ-ヴー]+'
    message = 'カタカナで入力してください！'


class ColorCodeRegexValidator(RegexValidator):
    """カラーコード専用バリデーター
    """
    regex = r'[0-9A-F]{6}'
    message = 'カラーコード形式で入力してください！'
