

def createTables(con):
    cursor = con.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS guild(
        guildName text,
        PRIMARY KEY (guildName))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS guildWar(
        guildName text,
        startDate text,
        type text,
        PRIMARY KEY (name))''')