import pymssql




def mssql_select(query):
    with pymssql.connect(host='192.168.1.1',
                         user='username',
                         password='pwd',
                         database='AutoHome') as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return [r for r in cursor]

def mssql_execute(query):
    with pymssql.connect(host='192.168.1.1',
                         user='username',
                         password='pwd',
                         database='AutoHome') as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            conn.commit()