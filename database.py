import sqlite3
import os
def connect(schema_file = "schema.sql", database_file = "database.db",restart=False):
    
    if restart:
        if os.path.isfile(database_file):
            os.remove(database_file)

    con = sqlite3.connect(database_file)

    try:
        cur = con.cursor()

        with open(schema_file) as f:
            sql = f.read() 
            cur.executescript(sql)
        
        cur.execute("SELECT * FROM ROLES;")
        roles = cur.fetchall()
        #print(roles)
        if roles==[]:
            cur.execute("INSERT INTO ROLES (ROLE_NAME) VALUES (?),(?);",("Admin","User"))
            cur.execute("INSERT INTO USER (ROLE_ID,USER_NAME,USER_PASSWORD) VALUES (?,?,?);",(1,"admin","1234"))
            con.commit()
        done = True
    except Exception as e:
        #print("ERROR: ",e)
        done =  False
    finally:
        if con:
            con.close()
    return done
if __name__ == "__main__":
    #connect(restart=1)
    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("INSERT INTO SECTIONS(SECTION_NAME) VALUES(?)",('SECTION1',))
        cur.execute("INSERT INTO PRODUCTS(PRODUCT_NAME,SECTION_ID, PRODUCT_PRICE) VALUES(?,?,?)",('PRODUCT1',1,299))
        con.commit()
        