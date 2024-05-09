from django import template

register = template.Library()

@register.filter
def percent_of(value, total):
    try:
        # Ensures the value is a float and prevent division by zero
        return 100 * float(value) / float(total) if total else 0
    except (ValueError, TypeError):
        return 0