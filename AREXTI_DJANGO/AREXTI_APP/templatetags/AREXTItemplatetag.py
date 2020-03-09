from django import template
from AREXTI_APP.models import ImagenHash, Imagen, ImagenDetalle

register = template.Library()

@register.filter
def img_hash_tags(tipo_hash, hashes):
    for hash in hashes:
        if hash.tipoHash == tipo_hash:
            return hash.valor
            break
    else:
        return None

@register.filter
def img_hash_tags2(tipo_hash, id):
    hashes = ImagenHash.objects.filter(imagen_id=id)
    for hash in hashes:
        if hash.tipoHash == tipo_hash:
            return hash.valor
            break
    else:
        return None

@register.simple_tag
def get_color_by_tipoImgen(tipoImagen):
    if tipoImagen == 'CHAT':
        color = 'primary'
    elif tipoImagen == 'MAIL':
        color = 'success'
    else:
        color = 'secondary'

    return color


@register.inclusion_tag('base/shared/ImagenDetalle.html')
def list_detail_text(imagenDetalles, tipoImagen, color):
    isChat = tipoImagen == 'CHAT'
    cabeceraText = ''
    mailText = ''
    imagenDetalleObjectMail = imagenDetalles.filter(tipoDetalle_id='MAIL')
    if imagenDetalleObjectMail:
        mailText = [p.texto for p in imagenDetalleObjectMail]

    if isChat:
        imagenDetalleObjectCabecera = imagenDetalles.filter(tipoDetalle_id='CABECERA')
        if imagenDetalleObjectCabecera:
            cabeceraText = imagenDetalleObjectCabecera[0]
            cabeceraText = cabeceraText.texto
    return {
        'imagenDetalle': imagenDetalles,
        'cabeceraText': cabeceraText,
        'mailText': mailText,
        'isChat': isChat,
        'color': color
    }



@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Return encoded URL parameters that are the same as the current
    request's parameters, only with the specified GET parameters added or changed.

    It also removes any empty parameters to keep things neat,
    so you can remove a parm by setting it to ``""``.

    For example, if you're on the page ``/things/?with_frosting=true&page=5``,
    then

    <a href="/things/?{% param_replace page=3 %}">Page 3</a>

    would expand to

    <a href="/things/?with_frosting=true&page=3">Page 3</a>

    Based on
    https://stackoverflow.com/questions/22734695/next-and-before-links-for-a-django-paginated-query/22735278#22735278
    """
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()

@register.filter(name='proper_paginate')
def proper_paginate(paginator, current_page, neighbors=3):
    if paginator.num_pages > 2*neighbors:
        start_index = max(1, current_page-neighbors)
        end_index = min(paginator.num_pages, current_page + neighbors)
        if end_index < start_index + 2*neighbors:
            end_index = start_index + 2*neighbors
        elif start_index > end_index - 2*neighbors:
            start_index = end_index - 2*neighbors
        if start_index < 1:
            end_index -= start_index
            start_index = 1
        elif end_index > paginator.num_pages:
            start_index -= (end_index-paginator.num_pages)
            end_index = paginator.num_pages
        page_list = [f for f in range(start_index, end_index+1)]
        return page_list[:(2*neighbors + 1)]
    return paginator.page_range
