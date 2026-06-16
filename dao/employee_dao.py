from database.connections import DatabaseConnection

class EmployeeDAO:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_employee_by_id(self, employee_id):
        """
        Looks up an employee by their ID and returns a dictionary with their details, or None if not found.
        """
        sql_query = """
            SELECT id_employee, empl_surname, empl_name, empl_patronymic, 
                   empl_role, salary, date_of_birth, date_of_start, 
                   phone_number, city, street, zip_code
            FROM Employee 
            WHERE id_employee = ?
        """
        conn = self.db.get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (employee_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row.id_employee, "surname": row.empl_surname, "name": row.empl_name,
                    "patronymic": row.empl_patronymic if row.empl_patronymic else "",
                    "role": row.empl_role, "salary": row.salary,
                    "date_of_birth": row.date_of_birth, "date_of_start": row.date_of_start,
                    "phone": row.phone_number, "city": row.city, "street": row.street, "zip": row.zip_code
                }
            return None
        except Exception as e:
            print(f"❌ Failed to retrieve employee {employee_id}: {e}")
            return None
        finally:
            conn.close() #close connection

    def update_employee(self, emp_id, emp_data, update_password=False):
        """
        Updates an employee's details in the database.
        If update_password=True, the password is also updated.
        """
        if update_password:
            sql_query = """
                UPDATE Employee SET 
                    empl_surname=?, empl_name=?, empl_patronymic=?, empl_role=?, 
                    salary=?, date_of_birth=?, date_of_start=?, phone_number=?, 
                    city=?, street=?, zip_code=?, password=?
                WHERE id_employee=?
            """
            params = (
                emp_data['surname'], emp_data['name'], emp_data['patronymic'], emp_data['role'],
                emp_data['salary'], emp_data['date_of_birth'], emp_data['date_of_start'], emp_data['phone'],
                emp_data['city'], emp_data['street'], emp_data['zip'], emp_data['password_hash'], emp_id
            )
        else:
            sql_query = """
                UPDATE Employee SET 
                    empl_surname=?, empl_name=?, empl_patronymic=?, empl_role=?, 
                    salary=?, date_of_birth=?, date_of_start=?, phone_number=?, 
                    city=?, street=?, zip_code=?
                WHERE id_employee=?
            """
            params = (
                emp_data['surname'], emp_data['name'], emp_data['patronymic'], emp_data['role'],
                emp_data['salary'], emp_data['date_of_birth'], emp_data['date_of_start'], emp_data['phone'],
                emp_data['city'], emp_data['street'], emp_data['zip'], emp_id
            )

        conn = self.db.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, params)
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Failed to update employee {emp_id}: {e}")
            return False
        finally:
            conn.close()

    def get_all_employees(self):
        """
        Get a list of all employees with their details sorted by surname.
        Returns a list of dictionaries, each representing an employee.
        """
        sql_query = """
            SELECT id_employee, empl_surname, empl_name, empl_patronymic, 
            empl_role, salary, date_of_birth, date_of_start, phone_number, city, street, zip_code
            FROM Employee 
            ORDER BY empl_surname ASC
        """
        
        conn = self.db.get_connection()
        if not conn:
            return []
            
        cursor = conn.cursor()
        employees_list = []
        try:
            cursor.execute(sql_query)
            rows = cursor.fetchall() 
            
            for row in rows:
                employees_list.append({
                    "id": row[0],
                    "surname": row[1],
                    "name": row[2],
                    "patronymic": row[3] if row[3] else "", 
                    "role": row[4],
                    "salary": row[5],
                    "date_of_birth": row[6],
                    "date_of_start": row[7],
                    "phone": row[8],
                    "city": row[9],
                    "street": row[10],
                    "zip_code": row[11]
                })
            return employees_list
        except Exception as e:
            print(f"❌ Exception while fetching all employees: {e}")
            return []
        finally:
            conn.close()

    def delete_employee(self, employee_id):
        """
        Deletes an employee from the database by their ID.
        Returns True if deletion was successful, False otherwise.
        """
        sql_query = "DELETE FROM Employee WHERE id_employee = ?"
        
        conn = self.db.get_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (employee_id,))
            conn.commit() #commit the changes to the database
            return True
        except Exception as e:
            print(f"❌ Failed to delete employee {employee_id}: {e}")
            return False
        finally:
            conn.close()

    def add_employee(self, emp_data):
        """
        Adds a new employee to the database.
        emp_data should be a dictionary containing all necessary fields, including 'password_hash'.
        """
        sql_query = """
            INSERT INTO Employee (
                id_employee, empl_surname, empl_name, empl_patronymic, 
                empl_role, salary, date_of_birth, date_of_start, 
                phone_number, city, street, zip_code, password
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        conn = self.db.get_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (
                emp_data['id'],
                emp_data['surname'],
                emp_data['name'],
                emp_data['patronymic'],
                emp_data['role'],
                emp_data['salary'],
                emp_data['date_of_birth'], 
                emp_data['date_of_start'],
                emp_data['phone'],
                emp_data['city'],
                emp_data['street'],
                emp_data['zip'],
                emp_data['password_hash'] 
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Failed to add an employee: {e}")
            return False
        finally:
            conn.close()

#test
if __name__ == "__main__":
    dao = EmployeeDAO()
    employee = dao.get_employee_by_id("24") 
    
    if employee:
        print(f"✅ Found employee: {employee['name']} {employee['surname']} ({employee['role']})")
    else:
        print("❌ Employee with the specified ID not found.")