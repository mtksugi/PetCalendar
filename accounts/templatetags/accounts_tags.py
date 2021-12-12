from django import template
register = template.Library()

GENDER_DIC = {1:'オス', 2:'メス', 3:'性別不明'}

@register.filter(name='gender_name')
def gender_name(gender):
    return GENDER_DIC[gender]


