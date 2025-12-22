from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Template filter to get item from dictionary"""
    if dictionary is None:
        return None
    return dictionary.get(key)

