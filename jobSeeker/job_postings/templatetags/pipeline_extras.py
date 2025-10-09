from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Template filter to lookup a key in a dictionary"""
    return dictionary.get(key, [])

@register.filter
def get(dictionary, key):
    """Template filter to get a value from a dictionary"""
    if dictionary is None:
        return []
    return dictionary.get(key, [])