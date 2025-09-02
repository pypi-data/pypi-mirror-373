from django import template
from django.utils.html import strip_tags

register = template.Library()


@register.filter
def stripAndsplit(string, sep):
    """Return the string split by sep.

    Example usage: {{ value|split:"/" }}
    """
    return strip_tags(string).split(sep)


@register.filter
def strip(string):
    """Return the string split by sep.

    Example usage: {{ value|split:"/" }}
    """
    return strip_tags(string)
