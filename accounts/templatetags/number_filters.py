# accounts/templatetags/number_filters.py
from django import template

register = template.Library()

@register.filter
def humanize_k(value):
    try:
        value = int(value)
    except (ValueError, TypeError):
        return value
    if value >= 1000:
        if value % 1000 == 0:
            return f"{value // 1000}k"
        else:
            return f"{value / 1000:.1f}k"
    return str(value)