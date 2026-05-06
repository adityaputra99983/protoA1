from django.template import Library

register = Library()

@register.filter
def split(value, arg):
    return [item.strip() for item in value.split(arg)]

@register.filter
def make_list(text):
    return list(str(text))