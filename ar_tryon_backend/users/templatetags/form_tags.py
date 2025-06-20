"""
Custom template tags for users app.
Template tags allow us to add custom functionality to our templates.
"""

from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    """
    Template filter to add CSS classes to form fields.
    Usage in templates: {{ form.field|add_class:"form-control" }}
    """
    return field.as_widget(attrs={"class": css_class})
