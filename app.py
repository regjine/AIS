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

if __name__ == '__main__':
    app.run(debug=True)