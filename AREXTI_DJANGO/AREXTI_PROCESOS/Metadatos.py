from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def get_decimal_coordinates(info):
    for key in ['Latitude', 'Longitude']:
        if 'GPS'+key in info and 'GPS'+key+'Ref' in info:
            e = info['GPS'+key]
            ref = info['GPS'+key+'Ref']
            info[key] = (e[0][0]/e[0][1] +
                         e[1][0]/e[1][1] / 60 +
                         e[2][0]/e[2][1] / 3600
                         ) * (-1 if ref in ['S', 'W'] else 1)

    if 'Latitude' in info and 'Longitude' in info:
        return [info['Latitude'], info['Longitude']]


def metadata_gps(gps_tags):
    gpsinfo = dict()
    for key in gps_tags.keys():
        tag_nombre = GPSTAGS.get(key, key)
        gpsinfo[tag_nombre] = gps_tags[key]
    return gpsinfo


def metadata_extraer():
    # img = Image.open("D:/PythonProyects/TesisPC/conGPS.jpg")
    img = Image.open("D:/PythonProyects/TesisPC/FotoProcessing.jpg")
    metadatos_dict = dict()

    # extrae los metadatos
    img_exif = img._getexif()

    if img_exif:
        img_exif_dict = dict(img_exif)

        for key, val in img_exif_dict.items():
            if key in TAGS:
                if TAGS[key] == 'GPSInfo':
                    gpsinfo = metadata_gps(val)
                elif TAGS[key] != 'MakerNote':
                    # print(f"{TAGS[key]}:{repr(val)}")
                    metadatos_dict.update({TAGS[key]: repr(val)})
        print("-----METADATA-----")
        print(metadatos_dict)
        print("-----GPS METADATA-----")
        print(gpsinfo)
    else:
        print("No posee metadata")

metadata_extraer()
#exif_GPS = get_decimal_coordinates(gpsinfo)