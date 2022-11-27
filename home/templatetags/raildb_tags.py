from django import template

register = template.Library()


@register.filter
def get_actual_distance(value):
    # 営業キロを 1/10 倍して表示
    str_value = str(value)
    if str_value == 'None':
        return ''
    elif len(str_value) == 1:
        return f'0.{str_value[-1]}'
    else:
        return f'{str_value[:-1]}.{str_value[-1]}'
