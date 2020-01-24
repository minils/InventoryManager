from django import template

register = template.Library()

@register.filter(name='limitend')
def limitend(value, arg):
    limit = int(arg)
    if limit >= len(value):
        return value
    else:
        return value[len(value)-limit:]
        
