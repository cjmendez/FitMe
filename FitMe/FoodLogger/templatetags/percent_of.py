from django import template

register = template.Library()

@register.filter
def percent_of(value, total):
    if total > 0:
        result = (float(value) / float(total)) * 100
    else:
        result = 0
    print(f"Percentage for {value} of {total}: {result}%")  # Debug output
    return result
