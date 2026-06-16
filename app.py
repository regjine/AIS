from flask import Flask, render_template, request, redirect, url_for, flash, session
from services.auth_service import AuthService

app = Flask(__name__)
app.secret_key = 'super_secret_key_zlagoda' 

auth_service = AuthService()

#main page (for authorised users)
@app.route('/')
def home():
    #send to login page if not logged in yet
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    #welcome page for logged in users
    return f"""
        <h1>Вітаємо, {session['user_name']}!</h1>
        <p>Ваша посада: <b>{session['user_role']}</b></p>
        <a href='/logout'>Вийти з системи</a>
    """

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

if __name__ == '__main__':
    app.run(debug=True)