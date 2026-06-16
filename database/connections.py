import pyodbc
import os

class DatabaseConnection:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #
        self.db_path = os.path.join(base_dir, 'zlagoda.accdb') #can be changed to the path of database file
        
        #connection string for MS Access
        self.connection_string = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            rf'DBQ={self.db_path};'
        )

    def get_connection(self):
        """Returns the object either connected to the database or None in case of error"""
        try:
            conn = pyodbc.connect(self.connection_string)
            return conn
        except pyodbc.Error as e:
            print(f"❌ Failed to connect to the database.\n{e}")
            return None

#test
if __name__ == "__main__":
    print(f"Looking for database at: {DatabaseConnection().db_path}")
    db = DatabaseConnection()
    test_conn = db.get_connection()
    
    if test_conn:
        print("✅ Successful connection to the ZLAGODA database!")
        test_conn.close()