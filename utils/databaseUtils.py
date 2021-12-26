import sqlite3
from pprint import pprint


def connectToDb(dbPath):
    return sqlite3.connect(dbPath)


def dictToSQL(values: dict):
    out = []
    for name, val in values.items():
        if isinstance(val, str):
            out.append(f'{name}="{val}"')
        else:
            out.append(f'{name}={val}')
    return ",".join(out)


def parseFetch(cursor):
    """Avoids returning only one atribute if the query only gets one result"""
    out = 'a'
    if (row := cursor.fetchall()) is not None:
        out = []
        for result in row:
            if isinstance(result, tuple):
                aux = []
                for x in result:
                    aux.append(x)
                if len(aux) > 1:
                    aux = tuple(aux)
            out.append(aux)
    return out if isinstance(out, list) else ""


def insert(con, tableName, values: list, valueNames: str = ""):
    aux = ['?']
    cursor = con.cursor()
    if len(valueNames) > 0:
        valueNames = f'({valueNames})'
    cursor.execute(
        "INSERT INTO {} {} VALUES ({})".format(
            tableName, valueNames, ",".join(aux*len(values))), values
    )
    con.commit()


def update(con, tableName, values: dict, where: str = '1=1'):
    cursor = con.cursor()
    values = dictToSQL(values)
    cursor.execute(
        f"UPDATE {tableName} SET {values} WHERE {where}"
    )
    con.commit()


def select(con, tableName, values: list = ['*'], where: str = '1=1'):
    cursor = con.cursor()
    values = ','.join(values)
    cursor.execute(
        f"SELECT {values} FROM {tableName} WHERE {where}"
    )
    return parseFetch(cursor)

def delete(con,tableName,where):
    cursor = con.cursor()
    cursor.execute(
        f"DELETE FROM {tableName} WHERE {where}"
    )
    con.commit()

def customSelect(con, SQLsentence: str):
    cursor = con.cursor()
    cursor.execute(SQLsentence)
    return parseFetch(cursor)


def customInsertUpdate(con, SQLsentence: str):
    cursor = con.cursor()
    cursor.execute(SQLsentence)
    con.commit()


def printTable(con, tableName: str):
    cursor = con.cursor()
    cursor.execute(f'SELECT * from {tableName}')
    pprint(cursor.fetchall())


def customSQL(con,sql):
    cursor = con.cursor()
    cursor.execute(sql,())
    con.commit()
    return parseFetch(cursor)
