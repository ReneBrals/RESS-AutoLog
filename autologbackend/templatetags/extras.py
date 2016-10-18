from django import template

register = template.Library()

@register.simple_tag(name='GET_string',takes_context=True)
def GET_string(context):
    return context['request'].GET.urlencode()