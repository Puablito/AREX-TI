from celery import shared_task
import os
# from AREXTI_DJANGO.AREXTI_PROCESOS import ImagenAcciones

@shared_task
def prueba_suma(x, y):
    return x + y


@shared_task
def prueba_json(hashes, perid, url):
	jsonObject = {}
	hashListObject = []

	for hash in hashes:
		hashObject = {"name": hash.id}
		hashListObject.append(hashObject)

	jsonObject["hashes"] = hashListObject
	jsonObject["pericia"] = perid
	jsonObject["urlFile"] = url
	jsonObject["tabFrom"] = "A"

	return jsonObject


# @shared_task
# def call_ImageProccess(x, y):
#
# 	return exec_proceso_principal()


@shared_task
def call_ChangeImageType(imagenId, imagenNombre, imagenTipoId):

	return True
	# return ImagenAcciones.cambiar_tipoimagen(imagenId, imagenNombre, imagenTipoId)


@shared_task
def getDirectories(baseDirectory, path, level):
	direct_list = path_to_dict(baseDirectory, path, level, 0)
	return direct_list


def path_to_dict(path, root, level, currentLevel):
	baseName = os.path.basename(path)
	rootName = os.path.join(root, baseName)
	d = {'text': baseName}
	d['p'] = rootName
	if os.path.isdir(path) and level > currentLevel:
		d['nodes'] = [path_to_dict(os.path.join(path, x), rootName, level, currentLevel+1) for x in os.listdir\
			             (path) if os.path.isdir(os.path.join(path, x))]
	return d

# def path_to_dict(path):
# 	d = {'text': os.path.basename(path)}
# 	if os.path.isdir(path):
# 		d['nodes'] = [path_to_dict(os.path.join(path,x)) for x in os.listdir\
#             (path) if os.path.isdir(os.path.join(path, x))]
# 	return d