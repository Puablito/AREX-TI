from celery import shared_task
import os
from AREXTI_PROCESOS import ImagenAcciones, ProcesoPrincipal


@shared_task(track_started=True)
def call_ProcessImage(periciaid, periciaNombre, tipoProceso, DirPrincipal, listaHash, periciaDir):
    return ProcesoPrincipal.proceso_Principal(periciaid, periciaNombre, tipoProceso, DirPrincipal, listaHash,
                                              periciaDir)


@shared_task
def call_ChangeImageType(imagenId, imagenNombre, imagenTipoId, periciaDir):
    return ImagenAcciones.cambiar_tipoimagen(imagenId, imagenNombre, imagenTipoId, periciaDir)


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
        d['nodes'] = [path_to_dict(os.path.join(path, x), rootName, level, currentLevel + 1) for x in os.listdir(path) if os.path.isdir(os.path.join(path, x))]
    return d
