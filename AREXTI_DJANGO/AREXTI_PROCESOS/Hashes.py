import hashlib
import cv2


def calcular_hashes(hash_dic, imagen_procesar):

    if 'md5' in hash_dic:
        hasher = hashlib.md5()
        hash_nro = obtener_hash(hasher, imagen_procesar)
        elemento = {'md5': hash_nro}
        hash_dic.update(elemento)

    if 'sha1' in hash_dic:
        hasher = hashlib.sha1()
        hash_nro = obtener_hash(hasher, imagen_procesar)
        elemento = {'sha1': hash_nro}
        hash_dic.update(elemento)

    if 'sha256' in hash_dic:
        hasher = hashlib.sha256()
        hash_nro = obtener_hash(hasher, imagen_procesar)
        elemento = {'sha256': hash_nro}
        hash_dic.update(elemento)

    if 'sha512' in hash_dic:
        hasher = hashlib.sha512()
        hash_nro = obtener_hash(hasher, imagen_procesar)
        elemento = {'sha512': hash_nro}
        hash_dic.update(elemento)

    return hash_dic


def obtener_hash(hasher, imagen_procesar):
    imagen_hash = cv2.imread(imagen_procesar)
    hasher.update(imagen_hash)
    return hasher.hexdigest()
