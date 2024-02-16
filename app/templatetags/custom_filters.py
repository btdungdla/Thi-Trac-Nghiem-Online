from django import template

register = template.Library()

@register.filter
def answer_class(answer, selected_answers,correct_answers):    
    if answer.id in selected_answers and answer.id in correct_answers:
        return 'select-correct'
    elif answer.id in correct_answers:
        return 'select-incorrect'
    else:
        return ''
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, None)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def int_to_char(value):
    return chr(value + 64)