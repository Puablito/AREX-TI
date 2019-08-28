import hashlib
import cv2


def calcular_hashes(hash_dic, imagen_with_path):

    if 'md5' in hash_dic:
        hasher = hashlib.md5()
        hash_nro = calcular_hash(hasher, imagen_with_path)
        elemento = {'md5': hash_nro}
        hash_dic.update(elemento)

    if 'sha1' in hash_dic:
        hasher = hashlib.sha1()
        hash_nro = calcular_hash(hasher, imagen_with_path)
        elemento = {'sha1': hash_nro}
        hash_dic.update(elemento)

    if 'sha256' in hash_dic:
        hasher = hashlib.sha256()
        hash_nro = calcular_hash(hasher, imagen_with_path)
        elemento = {'sha256': hash_nro}
        hash_dic.update(elemento)

    if 'sha512' in hash_dic:
        hasher = hashlib.sha512()
        hash_nro = calcular_hash(hasher, imagen_with_path)
        elemento = {'sha512': hash_nro}
        hash_dic.update(elemento)

    return hash_dic


def calcular_hash(hasher, imagen_with_path):
    imagen_hash = cv2.imread(imagen_with_path)
    hasher.update(imagen_hash)
    return hasher.hexdigest()
