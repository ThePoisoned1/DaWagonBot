import sqlite3
from utils import databaseUtils


def delete_team(con, teamId):
    databaseUtils.delete(con, 'team', f'name = "{teamId}"')


def insert_team(con, team):
    cursor = con.cursor()
    data = [team.name, ','.join(team.unitNames), ','.join(
            team.position), team.explanation, str(team.replacements), team.picUrl, ','.join(team.otherNames)]
    cursor.execute(
        'insert into team values (?,?,?,?,?,?,?)', data)
    con.commit()
