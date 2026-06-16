import bcrypt
from dao.employee_dao import EmployeeDAO

class AuthService:
    def __init__(self):
        self.employee_dao = EmployeeDAO()

    def login(self, employee_id, plain_password):
        """
        Checks login and password.
        Returns a dictionary with the login status and user data.
        """
        #look up the employee by ID
        employee = self.employee_dao.get_employee_by_id(employee_id)
        
        if not employee:
            return {"success": False, "message": "User with the specified ID not found."}
        
        #if the employee is found, check the password
        #get the hash from the database and encode the entered password to bytes
        hashed_password_from_db = employee["password_hash"].encode('utf-8')
        entered_password_bytes = plain_password.encode('utf-8')
        
        try:
            if bcrypt.checkpw(entered_password_bytes, hashed_password_from_db):
                return {
                    "success": True, 
                    "message": f"Welcome, {employee['name']} {employee['surname']}!",
                    "user_data": employee
                }
            else:
                return {"success": False, "message": "Incorrect password."}
        except ValueError:
            return {"success": False, "message": "System error: invalid password format in database."}

#test
if __name__ == "__main__":
    auth = AuthService()
    
    print("Test 1: Correct ID and password")
    result1 = auth.login("01", "password123")
    print(f"Status: {result1['success']}")
    print(f"Message: {result1['message']}")
    if result1['success']:
        print(f"Role in system: {result1['user_data']['role']}")
        
    print("\nTest 2: Incorrect Password")
    result2 = auth.login("01", "wrong_password")
    print(f"Status: {result2['success']}")
    print(f"Message: {result2['message']}")

    print("\nTest 3: Non-existent ID")
    result3 = auth.login("999", "password123")
    print(f"Status: {result3['success']}")
    print(f"Message: {result3['message']}")