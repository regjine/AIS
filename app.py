from flask import Flask, render_template, request, redirect, url_for, flash, session
from services.auth_service import AuthService

from dao.employee_dao import EmployeeDAO
employee_dao = EmployeeDAO()

app = Flask(__name__)
app.secret_key = 'super_secret_key_zlagoda' 

auth_service = AuthService()

#main page (for authorised users)
@app.route('/')
def home():
    #send to login page if not logged in yet
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        emp_id = request.form.get('employee_id')
        password = request.form.get('password')

        #login user via AuthService
        result = auth_service.login(emp_id, password)

        if result['success']:
            user = result['user_data']
            session['user_id'] = user['id']
            session['user_name'] = f"{user['name']} {user['surname']}"
            session['user_role'] = user['role']
            return redirect(url_for('home'))
        else:
            flash(result['message'])

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('login'))

@app.route('/employees')
def employees():
    #should be manager to access this page
    if session.get('user_role') != 'Manager':
        flash("Доступ заборонено! У вас немає прав для перегляду цієї сторінки.")
        return redirect(url_for('home'))
    
    all_emps = employee_dao.get_all_employees()
    return render_template('employees.html', employees=all_emps)

@app.route('/employees/delete/<emp_id>', methods=['POST'])
def delete_employee_route(emp_id):
    #privilege check: only manager can delete employees
    if session.get('user_role') != 'Manager':
        flash("У вас немає прав для виконання цієї дії!")
        return redirect(url_for('home'))
    
    #cannot delete yourself
    if emp_id == session.get('user_id'):
        flash("❌ Ви не можете видалити власного користувача, під яким зараз авторизовані!")
        return redirect(url_for('employees'))
    
    #delete 
    success = employee_dao.delete_employee(emp_id)
    
    if success:
        flash("✅ An employee has been successfully deleted.")
    else:
        flash("❌ Failed to delete an employee. They might be linked to existing receipts.")
        
    return redirect(url_for('employees'))

if __name__ == '__main__':
    app.run(debug=True)