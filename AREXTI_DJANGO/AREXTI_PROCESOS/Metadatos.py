from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

'''
    Este modulo se encarga de leer la metadata de la imagen, extraerla, procesarla para que sea legible y la devuelve
    dentro de un diccionario, si la imagen no posee metadatos el diccionario devuelto se encontrará vacio
'''


# Transforma las coordenadas del formato "((37, 1), (59, 1), (1228, 100))" a "-37.98674444444445"
def coordenadas_decimal(info):
    for key in ['Latitude', 'Longitude']:
        if 'GPS'+key in info and 'GPS'+key+'Ref' in info:
            e = info['GPS'+key]
            ref = info['GPS'+key+'Ref']
            info['GPS'+key] = (e[0][0]/e[0][1] +
                               e[1][0]/e[1][1] / 60 +
                               e[2][0]/e[2][1] / 3600
                               ) * (-1 if ref in ['S', 'W'] else 1)
    return info


# Extrae la información de GPS de la metadata de la imagen
def metadata_gps(gps_tags):
    gpsinfo = dict()
    for key in gps_tags.keys():
        tag_nombre = GPSTAGS.get(key, key)
        gpsinfo[tag_nombre] = gps_tags[key]
    return gpsinfo


# Metodo principal
def metadata_extraer(imagen_procesar):

    img = Image.open(imagen_procesar)
    metadatos_dict = dict()

    # extrae los metadatos
    img_exif = img._getexif()

    if img_exif:
        img_exif_dict = dict(img_exif)

        for key, val in img_exif_dict.items():
            if key in TAGS:
                if TAGS[key] == 'GPSInfo':
                    gpsinfo = metadata_gps(val)
                    gpsinfo = coordenadas_decimal(gpsinfo)
                elif TAGS[key] != 'MakerNote':
                    metadatos_dict.update({TAGS[key]: repr(val)})

        # agrego la información de GPS a los metadatos
        metadatos_dict.update(gpsinfo)  # HAY IMAGENES SIN GPSINFO, TIRA ERROR DE REFERENCIA. CONTROLAR CON IF?

    return metadatos_dict
