import psycopg2


import Config




class manager:
    connection = None

    def __init__(self):
        return

    def connect(self):
        try:
            self.connection = psycopg2.connect(dbname=Config.DB_name, user=Config.DB_user, password=Config.DB_password)
        except:
            print('can\'t conntect to DB')
            return False
        else:
            cur = self.connection.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS introduction_channels(server_id BIGINT NOT NULL,channel_id BIGINT NOT NULL, PRIMARY KEY (server_id) ); ")
            self.connection.commit()
            cur.close()
        return True

    def set_server_introduction_channel(self,server_id:int,channel_id:int):
        if self.connection:
            cur = self.connection.cursor()
            cur.execute("INSERT INTO introduction_channels (server_id, channel_id) VALUES(%s,%s) ON CONFLICT (server_id) DO UPDATE SET channel_id=%s;",(server_id,channel_id,channel_id))
            self.connection.commit()
            cur.close()


    def get_introduction_channels(self):
        if self.connection:
            data = {}
            cur = self.connection.cursor()
            cur.execute("SELECT * FROM introduction_channels")
            results = cur.fetchall()
            for result in results:
                data[result[0]] = result[1]
            cur.close()
            return (data)

    def get_introduction_channel(self,server_id):
        if self.connection:
            cur = self.connection.cursor()
            cur.execute("SELECT * FROM introduction_channels WHERE server_id=%s",(server_id,))
            result = cur.fetchone()
            cur.close()
            if result:
                return (result[1])
            else:
                return(None)

    def remove_introduction_channel(self,server_id):
        if self.connection:
            cur = self.connection.cursor()
            cur.execute("DELETE FROM introduction_channels WHERE server_id=%s ;",(server_id,))
            self.connection.commit()
            cur.close()

db_manager = manager()
