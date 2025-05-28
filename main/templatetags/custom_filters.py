from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def add(value, arg):
    """Add the arg to the value."""
    try:
        return str(value) + str(arg)
    except (ValueError, TypeError):
        return '' 