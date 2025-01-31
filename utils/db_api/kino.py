from datetime import datetime

from .database import Database


class KinoDatabase(Database):
    def create_table_kino(self):
        sql="""
            CREATE TABLE IF NOT EXISTS Kino(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id BIGINT NOT NULL UNIQUE,
                file_id VARCHAR(2000) NOT NULL,
                caption TEXT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME
                ); 
            """
        self.execute(sql,commit=True)

    def add_kino(self,post_id:int,file_id:str,caption:str):
        sql="""
            INSERT INTO Kino(post_id,file_id,caption,created_at,updated_at)
            VALUES(?,?,?,?,?)
            """
        timestamp=datetime.now().isoformat()
        self.execute(sql,parameters=(post_id,file_id,caption,timestamp,timestamp),commit=True)

    def update_kino_caption(self,new_caption:str,post_id:int):
        sql="""
            UPDATE Kino
            SET caption=?,updated_at=?,
            WHERE post_id=?
        
            """
        updated_time=datetime.now().isoformat()
        self.execute(sql,parameters=(new_caption,updated_time,post_id),commit=True)

    def get_kino_by_post_id(self,post_id:int):
        sql="""
            SELECT file_id,caption FROM Kino
            WHERE post_id=?
            """
        result=self.execute(sql,parameters=(post_id,),fetchone=True)
        if result:
            return {'file_id':result[0],'caption':result[1] if result[1] else None}
        return None  # If result is None, return None

    def delete_kino_by_postid(self,post_id:int):
        sql="""
            DELETE FROM Kino WHERE post_id=?    
        """
        self.execute(sql,parameters=(post_id,),commit=True)

    def count_kino(self):
        sql="""
            SELECT COUNT(*) FROM Kino
            """
        self.execute(sql,fetchone=True)

