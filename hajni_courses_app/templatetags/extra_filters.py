from django import template


register = template.Library()


@register.filter(name="add_class")
def add_class(field, class_name):
    return field.as_widget(attrs={"class": class_name})


@register.filter(name='split_by_star')
def split_by_star(value):
    return value.split('*')


@register.filter(name='split_by_parenthesis')
def split_by_parenthesis(value):
    return value.split('(')


@register.filter(name='format_number')
def format_number(number):
    return f"{number:,.0f}"
