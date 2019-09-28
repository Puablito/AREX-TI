import hashlib
import cv2


def calcular_hashes(hash_dic, imagen_procesar):

    keys = hash_dic.keys()
    for key in keys:
        hash_nro = obtener_hash(key.lower(), imagen_procesar)
        elemento = {key: hash_nro}
        hash_dic.update(elemento)

    return hash_dic


def obtener_hash(hash, imagen_procesar):
    hasher = hashlib.new(hash)
    imagen_hash = cv2.imread(imagen_procesar)
    hasher.update(imagen_hash)
    return hasher.hexdigest()




# listado_hashes = {"mD3": "", "sHa1": "", "SHA256": ""}
# listado_hashes = calcular_hashes(listado_hashes, "F:\PythonProyects\SegmentacionIMG\Imagenes\Whatsapp.jpg")
# print(listado_hashes)
