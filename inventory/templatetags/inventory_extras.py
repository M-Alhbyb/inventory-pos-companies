from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the argument to the value."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''
