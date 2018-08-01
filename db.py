import sqlite3

SCHEMA_PATH = 'schema.sql'

def main():
    # db creation
    conn = sqlite3.connect('iot.db')
    with open(SCHEMA_PATH, mode='r') as f:
        conn.executescript(f.read())

    for c in (repr(i) for i in range(12)):
        conn.execute("insert into autorise(id_badge) values (?);", (c, ))

    for row in conn.execute("select * from autorise;"):
        print(row)
    
    pass

if __name__ == '__main__':
    main()
