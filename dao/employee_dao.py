from database.connections import DatabaseConnection

class EmployeeDAO:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_employee_by_id(self, employee_id):
        """Looks up an employee by their ID and returns a dictionary with their details, or None if not found."""

        sql_query = "SELECT id_employee, empl_surname, empl_name, empl_role, password FROM Employee WHERE id_employee = ?"
        
        conn = self.db.get_connection()
        if not conn:
            return None
            
        cursor = conn.cursor()
        try:
            cursor.execute(sql_query, (employee_id,))
            row = cursor.fetchone() #this will return a single row or None if no match is found
            
            if row:
                return {
                    "id": row[0],
                    "surname": row[1],
                    "name": row[2],
                    "role": row[3],
                    "password_hash": row[4]
                }
            return None
        except Exception as e:
            print(f"❌ Failed to execute SQL query in EmployeeDAO:\n{e}")
            return None
        finally:
            conn.close() #close connection

#test
if __name__ == "__main__":
    dao = EmployeeDAO()
    employee = dao.get_employee_by_id("24") 
    
    if employee:
        print(f"✅ Found employee: {employee['name']} {employee['surname']} ({employee['role']})")
    else:
        print("❌ Employee with the specified ID not found.")