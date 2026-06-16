from flask import Flask, render_template, request, redirect, url_for, flash, session
from services.auth_service import AuthService

from dao.employee_dao import EmployeeDAO
employee_dao = EmployeeDAO()

from datetime import datetime, date, timedelta
import bcrypt

from dao.category_dao import CategoryDAO
category_dao = CategoryDAO()

from dao.product_dao import ProductDAO
product_dao = ProductDAO()

from dao.store_product_dao import StoreProductDAO
store_product_dao = StoreProductDAO()

from dao.customer_dao import CustomerDAO
customer_dao = CustomerDAO()

from dao.check_dao import CheckDAO
check_dao = CheckDAO()

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
    
@app.route('/employees/add', methods=['GET', 'POST'])
def add_employee_route():
    if session.get('user_role') != 'Manager':
        flash("Доступ заборонено!")
        return redirect(url_for('home'))

    if request.method == 'POST':
        #gather data from the form
        emp_id = request.form.get('id')
        surname = request.form.get('surname')
        name = request.form.get('name')
        patronymic = request.form.get('patronymic')
        role = request.form.get('role')
        salary = float(request.form.get('salary'))
        phone = request.form.get('phone')
        city = request.form.get('city')
        street = request.form.get('street')
        zip_code = request.form.get('zip')
        plain_password = request.form.get('password')
        
        #parsing date strings to date objects
        dob_str = request.form.get('date_of_birth')
        dos_str = request.form.get('date_of_start')
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        dos = datetime.strptime(dos_str, '%Y-%m-%d').date()

        #Корпоративні обмеження    
        #1. Перевірка довжини телефону (max 13 символів)
        if len(phone) > 13:
            flash("❌ Помилка: Номер телефону не може перевищувати 13 символів!")
            return render_template('add_employee.html')

        #2. Перевірка віку (мінімум 18 років)
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 18:
            flash("❌ Помилка: Співробітник не може бути молодшим за 18 років!")
            return render_template('add_employee.html')
            
        #3. Перевірка на від'ємні значення зарплати
        if salary < 0:
            flash("❌ Помилка: Зарплата не може бути від'ємною!")
            return render_template('add_employee.html')

        #hash the password before saving to database
        hashed = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        #make a dictionary with all employee data to pass to DAO
        new_emp = {
            "id": emp_id, "surname": surname, "name": name, "patronymic": patronymic,
            "role": role, "salary": salary, "date_of_birth": dob, "date_of_start": dos,
            "phone": phone, "city": city, "street": street, "zip": zip_code,
            "password_hash": hashed
        }

        #write to Access
        if employee_dao.add_employee(new_emp):
            flash(f"✅ Співробітника {surname} {name} додано!!")
            return redirect(url_for('employees'))
        else:
            flash("❌ Не вдалося додати нового співробітника. Можливе дублювання ID.")
            return render_template('add_employee.html')

    return render_template('add_employee.html')

@app.route('/employees/edit/<emp_id>', methods=['GET', 'POST'])
def edit_employee_route(emp_id):
    if session.get('user_role') != 'Manager':
        flash("Доступ заборонено!")
        return redirect(url_for('home'))

    #get current employee data to pre-fill the form
    emp = employee_dao.get_employee_by_id(emp_id)
    if not emp:
        flash("❌ Співробітника не знайдено!")
        return redirect(url_for('employees'))

    if request.method == 'POST':
        surname = request.form.get('surname')
        name = request.form.get('name')
        patronymic = request.form.get('patronymic')
        role = request.form.get('role')
        salary = float(request.form.get('salary'))
        phone = request.form.get('phone')
        city = request.form.get('city')
        street = request.form.get('street')
        zip_code = request.form.get('zip')
        plain_password = request.form.get('password')
        
        dob = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date()
        dos = datetime.strptime(request.form.get('date_of_start'), '%Y-%m-%d').date()

        if len(phone) > 13:
            flash("❌ Помилка: Номер телефону не може перевищувати 13 символів!")
            return render_template('edit_employee.html', emp=emp)

        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 18:
            flash("❌ Помилка: Співробітник не може бути молодшим за 18 років!")
            return render_template('edit_employee.html', emp=emp)
            
        if salary < 0:
            flash("❌ Помилка: Зарплата не може бути від'ємною!")
            return render_template('edit_employee.html', emp=emp)

        updated_data = {
            "surname": surname, "name": name, "patronymic": patronymic,
            "role": role, "salary": salary, "date_of_birth": dob, "date_of_start": dos,
            "phone": phone, "city": city, "street": street, "zip": zip_code
        }

        #if a new password is provided, hash it and include in the update
        update_password = False
        if plain_password and plain_password.strip() != "":
            hashed = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            updated_data["password_hash"] = hashed
            update_password = True

        #update the employee in the database
        if employee_dao.update_employee(emp_id, updated_data, update_password):
            #if the edited employee is the currently logged-in user, update their session name
            if emp_id == session.get('user_id'):
                session['user_name'] = f"{name} {surname}"
            
            flash(f"✅ Дані співробітника {surname} успішно оновлено!")
            return redirect(url_for('employees'))
        else:
            flash("❌ Не вдалося оновити дані співробітника. Будь ласка, перевірте введені дані.")
            return render_template('edit_employee.html', emp=emp)

    return render_template('edit_employee.html', emp=emp)

@app.route('/categories')
def categories():
    if not session.get('user_role'):
        flash("Будь ласка, авторизуйтеся в системі!")
        return redirect(url_for('login'))
        
    all_cats = category_dao.get_all_categories() 
    return render_template('categories.html', categories=all_cats)

@app.route('/categories/add', methods=['GET', 'POST'])
def add_category_route():
    if session.get('user_role') != 'Manager':
        flash("Доступ заборонено!")
        return redirect(url_for('categories'))

    if request.method == 'POST':
        cat_id = request.form.get('category_id')
        cat_name = request.form.get('category_name')

        if not cat_id or not cat_name or cat_name.strip() == "":
            flash("❌ Усі поля обов'язкові для заповнення!")
            return render_template('add_category.html')

        if int(cat_id) <= 0:
            flash("❌ ID категорії має бути більшим за 0!")
            return render_template('add_category.html')

        if category_dao.add_category(int(cat_id), cat_name.strip()):
            return redirect(url_for('categories'))
        else:
            flash("❌ Не вдалося зберегти категорію. Можливо, категорія з таким ID вже існує в системі.")
            return render_template('add_category.html')

    return render_template('add_category.html')

@app.route('/categories/edit/<int:cat_id>', methods=['GET', 'POST'])
def edit_category_route(cat_id):
    if session.get('user_role') != 'Manager':
        flash("Доступ заборонено!")
        return redirect(url_for('categories'))

    cat = category_dao.get_category_by_id(cat_id)
    if not cat:
        flash("❌ Категорію не знайдено!")
        return redirect(url_for('categories'))

    if request.method == 'POST':
        new_name = request.form.get('category_name')

        if not new_name or new_name.strip() == "":
            flash("❌ Назва категорії не може бути порожньою!")
            return render_template('edit_category.html', cat=cat)

        if category_dao.update_category(cat_id, new_name.strip()):
            return redirect(url_for('categories'))
        else:
            flash("❌ Не вдалося зберегти зміни в базі даних.")
            return render_template('edit_category.html', cat=cat)

    return render_template('edit_category.html', cat=cat)

@app.route('/categories/delete/<int:cat_id>', methods=['POST'])
def delete_category_route(cat_id):
    if session.get('user_role') != 'Manager':
        flash("Доступ заборонено!")
        return redirect(url_for('categories'))

    if not category_dao.delete_category(cat_id):
        flash("❌ Не вдалося видалити категорію. Можливо, до неї прив'язані існуючі товари.")
        
    return redirect(url_for('categories'))

@app.route('/products')
def products():
    if not session.get('user_role'):
        flash("Будь ласка, авторизуйтеся в системі!")
        return redirect(url_for('login'))
        
    all_prods = product_dao.get_all_products()
    return render_template('products.html', products=all_prods)

@app.route('/products/add', methods=['GET', 'POST'])
def add_product_route():
    if session.get('user_role') != 'Manager':
        flash("Доступ заборонено!")
        return redirect(url_for('products'))

    categories_list = category_dao.get_all_categories()

    if request.method == 'POST':
        prod_id = request.form.get('id')
        name = request.form.get('name')
        category_number = request.form.get('category_number')
        characteristics = request.form.get('characteristics')

        if not prod_id or not name or not category_number:
            flash("❌ Будь ласка, заповніть усі обов'язкові поля!")
            return render_template('add_product.html', categories=categories_list)

        if int(prod_id) <= 0:
            flash("❌ ID товару має бути більшим за 0!")
            return render_template('add_product.html', categories=categories_list)

        new_prod = {
            "id": int(prod_id),
            "category_number": int(category_number),
            "name": name.strip(),
            "characteristics": characteristics.strip() if characteristics else ""
        }

        if product_dao.add_product(new_prod):
            flash(f"✅ Товар {name} успішно додано до каталогу!")
            return redirect(url_for('products'))
        else:
            flash("❌ Не вдалося зберегти товар. Можливо, товар з таким ID вже існує.")
            return render_template('add_product.html', categories=categories_list)

    return render_template('add_product.html', categories=categories_list)

@app.route('/products/edit/<int:prod_id>', methods=['GET', 'POST'])
def edit_product_route(prod_id):
    if session.get('user_role') != 'Manager':
        flash("Доступ заборонено!")
        return redirect(url_for('products'))

    prod = product_dao.get_product_by_id(prod_id)
    if not prod:
        flash("❌ Товар не знайдено в каталозі!")
        return redirect(url_for('products'))

    categories_list = category_dao.get_all_categories()

    if request.method == 'POST':
        name = request.form.get('name')
        category_number = request.form.get('category_number')
        characteristics = request.form.get('characteristics')

        if not name or not category_number:
            flash("❌ Усі обов'язкові поля мають бути заповнені!")
            return render_template('edit_product.html', prod=prod, categories=categories_list)

        updated_prod = {
            "category_number": int(category_number),
            "name": name.strip(),
            "characteristics": characteristics.strip()
        }

        if product_dao.update_product(prod_id, updated_prod):
            flash(f"✅ Дані товару {name} успішно оновлено!")
            return redirect(url_for('products'))
        else:
            flash("❌ Не вдалося зберегти зміни в базі даних.")
            return render_template('edit_product.html', prod=prod, categories=categories_list)

    return render_template('edit_product.html', prod=prod, categories=categories_list)


@app.route('/products/delete/<int:prod_id>', methods=['POST'])
def delete_product_route(prod_id):
    if session.get('user_role') != 'Manager':
        flash("Доступ заборонено!")
        return redirect(url_for('products'))

    if not product_dao.delete_product(prod_id):
        flash("❌ Не вдалося видалити товар. Можливо, на нього посилаються товари, які вже лежать на полицях магазину.")
        
    return redirect(url_for('products'))

@app.route('/store_products')
def store_products():
    if not session.get('user_role'):
        flash("Будь ласка, авторизуйтеся в системі!")
        return redirect(url_for('login'))
        
    all_store_items = store_product_dao.get_all_store_products()
    return render_template('store_products.html', store_products=all_store_items)

@app.route('/store_products/add', methods=['GET', 'POST'])
def add_store_product_route():
    if session.get('user_role') != 'Manager':
        flash("Доступ заборонено! Тільки менеджер може додавати товари в магазин.")
        return redirect(url_for('store_products'))

    #list of products from Product table to choose from when adding a new Store_Product
    catalog_products = product_dao.get_all_products()

    if request.method == 'POST':
        upc = request.form.get('upc')
        upc_prom = request.form.get('upc_prom')
        product_id = request.form.get('product_id')
        price = request.form.get('price')
        quantity = request.form.get('quantity')
        is_promo = True if request.form.get('is_promo') == 'on' else False

        if not upc or not product_id or not price or not quantity:
            flash("❌ Будь ласка, заповніть усі обов'язкові поля!")
            return render_template('add_store_product.html', catalog=catalog_products)

        try:
            clean_price = float(price.replace(',', '.'))
            clean_quantity = int(quantity)
        except ValueError:
            flash("❌ Некоректний формат ціни або кількості!")
            return render_template('add_store_product.html', catalog=catalog_products)

        new_store_item = {
            "upc": upc.strip(),
            "upc_prom": upc_prom.strip() if upc_prom else None,
            "product_id": int(product_id),
            "price": clean_price,
            "quantity": clean_quantity,
            "is_promo": is_promo
        }

        if store_product_dao.add_store_product(new_store_item):
            flash(f"✅ Товар з UPC {upc} успішно виставлено на полиці магазину!")
            return redirect(url_for('store_products'))
        else:
            flash("❌ Не вдалося додати товар. Перевірте, чи унікальний UPC (можливо, такий штрих-код вже є в базі).")
            return render_template('add_store_product.html', catalog=catalog_products)

    return render_template('add_store_product.html', catalog=catalog_products)

@app.route('/store_products/edit/<upc>', methods=['GET', 'POST'])
def edit_store_product_route(upc):
    if session.get('user_role') != 'Manager':
        flash("Доступ заборонено!")
        return redirect(url_for('store_products'))

    sp_item = store_product_dao.get_store_product_by_upc(upc)
    if not sp_item:
        flash("❌ Товар з таким UPC не знайдено в магазині!")
        return redirect(url_for('store_products'))

    catalog_products = product_dao.get_all_products()

    if request.method == 'POST':
        upc_prom = request.form.get('upc_prom')
        product_id = request.form.get('product_id')
        price = request.form.get('price')
        quantity = request.form.get('quantity')
        is_promo = True if request.form.get('is_promo') == 'on' else False

        if not product_id or not price or not quantity:
            flash("❌ Усі обов'язкові поля мають бути заповнені!")
            return render_template('edit_store_product.html', item=sp_item, catalog=catalog_products)

        try:
            clean_price = float(price.replace(',', '.'))
            clean_quantity = int(quantity)
        except ValueError:
            flash("❌ Некоректний формат ціни або кількості!")
            return render_template('edit_store_product.html', item=sp_item, catalog=catalog_products)

        updated_sp = {
            "upc_prom": upc_prom.strip() if upc_prom else None,
            "product_id": int(product_id),
            "price": clean_price,
            "quantity": clean_quantity,
            "is_promo": is_promo
        }

        if store_product_dao.update_store_product(upc, updated_sp):
            flash(f"✅ Дані про товар з UPC {upc} успішно оновлено!")
            return redirect(url_for('store_products'))
        else:
            flash("❌ Не вдалося зберегти зміни в базі даних.")
            return render_template('edit_store_product.html', item=sp_item, catalog=catalog_products)

    return render_template('edit_store_product.html', item=sp_item, catalog=catalog_products)


@app.route('/store_products/delete/<upc>', methods=['POST'])
def delete_store_product_route(upc):
    if session.get('user_role') != 'Manager':
        flash("Доступ заборонено!")
        return redirect(url_for('store_products'))

    if store_product_dao.delete_store_product(upc):
        flash("✅ Товар успішно прибрано з полиць магазину!")
    else:
        flash("❌ Не вдалося видалити товар. Можливо, цей штрих-код фігурує в існуючих чеках продажів.")
        
    return redirect(url_for('store_products'))

@app.route('/customers')
def customers():
    if not session.get('user_role'):
        flash("Будь ласка, авторизуйтеся в системі!")
        return redirect(url_for('login'))
        
    all_custs = customer_dao.get_all_customers()
    return render_template('customers.html', customers=all_custs)

@app.route('/customers/add', methods=['GET', 'POST'])
def add_customer_route():
    if not session.get('user_role'):
        flash("Авторизуйтеся в системі!")
        return redirect(url_for('login'))

    if request.method == 'POST':
        card_number = request.form.get('card_number')
        surname = request.form.get('surname')
        name = request.form.get('name')
        patronymic = request.form.get('patronymic')
        phone = request.form.get('phone')
        city = request.form.get('city')
        street = request.form.get('street')
        zip_code = request.form.get('zip_code')
        percent = request.form.get('percent')

        if not card_number or not surname or not name or not phone or not percent:
            flash("❌ Заповніть усі обов'язкові поля.")
            return render_template('add_customer.html')

        new_cust = {
            "card_number": card_number.strip(),
            "surname": surname.strip(),
            "name": name.strip(),
            "patronymic": patronymic.strip() if patronymic else "",
            "phone": phone.strip(),
            "city": city.strip() if city else "",
            "street": street.strip() if street else "",
            "zip_code": zip_code.strip() if zip_code else "",
            "percent": int(percent)
        }

        if customer_dao.add_customer(new_cust):
            flash(f"✅ Клієнта {surname} {name} успішно зареєстровано!")
            return redirect(url_for('customers'))
        else:
            flash("❌ Не вдалося створити картку. Можливо, такий номер картки вже зайнятий.")
            return render_template('add_customer.html')

    return render_template('add_customer.html')


@app.route('/customers/edit/<card_number>', methods=['GET', 'POST'])
def edit_customer_route(card_number):
    if not session.get('user_role'):
        flash("Авторизуйтеся в системі!")
        return redirect(url_for('login'))

    cust = customer_dao.get_customer_by_card(card_number)
    if not cust:
        flash("❌ Клієнта не знайдено!")
        return redirect(url_for('customers'))

    if request.method == 'POST':
        surname = request.form.get('surname')
        name = request.form.get('name')
        patronymic = request.form.get('patronymic')
        phone = request.form.get('phone')
        city = request.form.get('city')
        street = request.form.get('street')
        zip_code = request.form.get('zip_code')
        percent = request.form.get('percent')

        if not surname or not name or not phone or not percent:
            flash("❌ Обов'язкові поля не можуть бути порожніми!")
            return render_template('edit_customer.html', cust=cust)

        updated_cust = {
            "surname": surname.strip(),
            "name": name.strip(),
            "patronymic": patronymic.strip() if patronymic else "",
            "phone": phone.strip(),
            "city": city.strip() if city else "",
            "street": street.strip() if street else "",
            "zip_code": zip_code.strip() if zip_code else "",
            "percent": int(percent)
        }

        if customer_dao.update_customer(card_number, updated_cust):
            flash(f"✅ Дані клієнта {surname} успішно оновлено!")
            return redirect(url_for('customers'))
        else:
            flash("❌ Не вдалося зберегти зміни.")
            return render_template('edit_customer.html', cust=cust)

    return render_template('edit_customer.html', cust=cust)


@app.route('/customers/delete/<card_number>', methods=['POST'])
def delete_customer_route(card_number):
    if session.get('user_role') != 'Manager':
        flash("Доступ заборонено! Лише менеджер може видаляти клієнтів.")
        return redirect(url_for('customers'))

    if customer_dao.delete_customer(card_number):
        flash("✅ Картку клієнта успішно видалено з бази.")
    else:
        flash("❌ Не вдалося видалити картку. Можливо, цей клієнт вже робив покупки й зафіксований у чеках.")
        
    return redirect(url_for('customers'))

@app.route('/checks')
def checks():
    if not session.get('user_role'):
        flash("Будь ласка, авторизуйтеся в системі!")
        return redirect(url_for('login'))
        
    all_checks = check_dao.get_all_checks()
    return render_template('checks.html', checks=all_checks)

from datetime import datetime, timedelta
from dao.store_product_dao import StoreProductDAO
from dao.customer_dao import CustomerDAO

store_product_dao = StoreProductDAO()
customer_dao = CustomerDAO()

@app.route('/checks/add', methods=['GET', 'POST'])
def add_check_route():
    if session.get('user_role') != 'Cashier':
        flash("❌ Доступ заборонено! Тільки касири можуть створювати чеки.")
        return redirect(url_for('checks'))

    store_products = store_product_dao.get_all_store_products()
    customers = customer_dao.get_all_customers()

    if request.method == 'POST':
        check_number = request.form.get('check_number').strip()
        card_number = request.form.get('card_number')
        date_str = request.form.get('print_date')
        
        upcs = request.form.getlist('upc[]')
        quantities = request.form.getlist('quantity[]')

        if not check_number or not date_str or not upcs:
            flash("❌ Заповніть номер чека, дату та додайте хоча б один товар!")
            return render_template('add_check.html', products=store_products, customers=customers)
        
        #no more than 3 years ago
        try:
            print_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash("❌ Некоректний формат дати!")
            return render_template('add_check.html', products=store_products, customers=customers)

        three_years_ago = datetime.now() - timedelta(days=3 * 365)
        if print_date < three_years_ago:
            flash(f"❌ Помилка валідації: Архів чеків зберігається лише 3 роки! Дата не може бути ранішою за {three_years_ago.strftime('%d.%m.%Y')}.")
            return render_template('add_check.html', products=store_products, customers=customers)
        if print_date > datetime.now():
            flash("❌ Помилка валідації: Не можна пробити чек майбутнім часом!")
            return render_template('add_check.html', products=store_products, customers=customers)

        #total coast
        sales_list = []
        total_sum = 0.0


        prod_dict = {p['upc']: p for p in store_products}

        for i in range(len(upcs)):
            current_upc = upcs[i]
            if not current_upc: continue
            
            try:
                qty = int(quantities[i])
                if qty <= 0: raise ValueError()
            except ValueError:
                flash("❌ Кількість товару повинна бути цілим додатним числом!")
                return render_template('add_check.html', products=store_products, customers=customers)

            if current_upc not in prod_dict:
                flash(f"❌ Товар з UPC {current_upc} не знайдено в магазині.")
                return render_template('add_check.html', products=store_products, customers=customers)

            item_data = prod_dict[current_upc]
            
            #check if enough quantity is available in stock
            if item_data['quantity'] < qty:
                flash(f"❌ Недостатньо товару '{item_data['product_name']}' на складі! В наявності лише {item_data['quantity']} шт.")
                return render_template('add_check.html', products=store_products, customers=customers)

            item_price = float(item_data['price'])
            total_sum += item_price * qty

            sales_list.append({
                "upc": current_upc,
                "quantity": qty,
                "price": item_price
            })

        discount_percent = 0
        customer_data = customer_dao.get_customer_by_card(card_number)
        if customer_data:
            discount_percent = int(customer_data['percent'])

        #apply discount
        if discount_percent > 0:
            total_sum = total_sum * (1 - (discount_percent / 100.0))

        vat_value = (total_sum * 20) / 120

        check_data = {
            "check_number": check_number,
            "id_employee": session.get('user_id'),  #auto-fill with the logged-in cashier's ID
            "card_number": card_number if card_number != "" else None,
            "print_date": print_date,
            "sum_total": total_sum,
            "vat": vat_value
        }

        if check_dao.create_check_with_sales(check_data, sales_list):
            flash(f"✅ Чек №{check_number} успішно збережено")
            return redirect(url_for('checks'))
        else:
            flash("❌ Помилка бази даних. Перевірте, чи унікальний номер чека.")
            return render_template('add_check.html', products=store_products, customers=customers)

    return render_template('add_check.html', products=store_products, customers=customers)

@app.route('/checks/delete/<check_number>', methods=['POST'])
def delete_check_route(check_number):
    if session.get('user_role') != 'Manager':
        flash("❌ Доступ заборонено! Тільки менеджер може анулювати та видаляти чеки.")
        return redirect(url_for('checks'))

    if check_dao.delete_check(check_number):
        flash(f"✅ Чек №{check_number} успішно анульовано. Товари повернуто на склад!")
    else:
        flash("❌ Не вдалося видалити чек через помилку бази даних.")
        
    return redirect(url_for('checks'))

@app.route('/checks/view/<check_number>')
def view_check_route(check_number):
    """
    Маршрут для детального перегляду фіскального чека (товарів у ньому).
    """
    if not session.get('user_role'):
        flash("Будь ласка, авторизуйтеся в системі!")
        return redirect(url_for('login'))

    check_info = check_dao.get_check_by_number(check_number)
    if not check_info:
        flash("❌ Чек не знайдено в архіві системи!")
        return redirect(url_for('checks'))

    check_items = check_dao.get_check_details(check_number)

    return render_template('view_check.html', check=check_info, items=check_items)

if __name__ == '__main__':
    app.run(debug=True)