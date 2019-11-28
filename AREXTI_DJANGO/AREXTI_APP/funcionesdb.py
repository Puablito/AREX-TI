from django.db import connection


def consulta(query, params=None, diccionario=True):
    try:
        cursor = connection.cursor()
        cursor.callproc(query, params)
        # convierte el resultado en un diccionario
        if diccionario:
            result = []
            columns = tuple([d[0] for d in cursor.description])
            for row in cursor:
                result.append(dict(zip(columns, row)))
            return result
        else:
            reultado = cursor.fetchall()
            return reultado
    except Exception as e:
        cursor.close()
