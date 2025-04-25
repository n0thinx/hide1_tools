# custom_filters.py

from django import template

register = template.Library()

@register.filter
def format_size(value):
    try:
        # Convert imageSize to an integer
        size_in_bytes = int(value)
        # Convert bytes to megabytes (1 MB = 1024 * 1024 bytes)
        size_in_mb = size_in_bytes / (1024 * 1024)
        # Format the size to two decimal places
        return '{:.2f} MB'.format(size_in_mb)
    except ValueError:
        return value  # Return the original value if conversion fails
