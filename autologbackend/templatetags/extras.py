from django import template

register = template.Library()

@register.simple_tag(name='GET_string',takes_context=True)
def GET_string(context):
    query = context['request'].GET.dict()

    return '?' + '&'.join([ str(k)+"="+str(v) for k,v in query.iteritems()])