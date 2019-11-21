from django.db import connection


def consulta(query, params=None):
    try:
        cursor = connection.cursor()
        cursor.callproc(query, params)
        # convierte el resultado en un diccionario
        result = []
        columns = tuple([d[0] for d in cursor.description])
        for row in cursor:
            result.append(dict(zip(columns, row)))
        return result
    except Exception as e:
        cursor.close()
