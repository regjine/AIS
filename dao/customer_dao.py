from database.connections import DatabaseConnection

class CustomerDAO:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_customers(self):
        sql_query = """
            SELECT card_number, cust_surname, cust_name, cust_patronymic, 
                   phone_number, city, street, zip_code, [percent]
            FROM Customer_Card
            ORDER BY cust_surname ASC
        """
        conn = self.db.get_connection()
        if not conn:
            return []
            
        customers_list = []
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            
            for row in rows:
                customers_list.append({
                    "card_number": row.card_number,
                    "surname": row.cust_surname,
                    "name": row.cust_name,
                    "patronymic": row.cust_patronymic if row.cust_patronymic else "",
                    "phone": row.phone_number,
                    "city": row.city if row.city else "—",
                    "street": row.street if row.street else "—",
                    "zip_code": row.zip_code if row.zip_code else "—",
                    "percent": row.percent
                })
            return customers_list
        except Exception as e:
            print(f"❌ Exception while executing SQL query (get_all_customers): {e}")
            return []
        finally:
            conn.close()

    def add_customer(self, cust_data):
        """
        Додає нову картку клієнта в базу даних.
        """
        sql_query = """
            INSERT INTO Customer_Card (card_number, cust_surname, cust_name, cust_patronymic, phone_number, city, street, zip_code, [percent])
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        conn = self.db.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (
                cust_data['card_number'],
                cust_data['surname'],
                cust_data['name'],
                cust_data['patronymic'] if cust_data['patronymic'].strip() != "" else "",
                cust_data['phone'],
                cust_data['city'] if cust_data['city'].strip() != "" else "—",
                cust_data['street'] if cust_data['street'].strip() != "" else "—",
                cust_data['zip_code'] if cust_data['zip_code'].strip() != "" else "—",
                cust_data['percent']
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Помилка додавання клієнта: {e}")
            return False
        finally:
            conn.close()

    def get_customer_by_card(self, card_number):
        sql_query = "SELECT * FROM Customer_Card WHERE card_number = ?"
        conn = self.db.get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (card_number,))
            row = cursor.fetchone()
            if row:
                return {
                    "card_number": row.card_number,
                    "surname": row.cust_surname,
                    "name": row.cust_name,
                    "patronymic": row.cust_patronymic if row.cust_patronymic else "",
                    "phone": row.phone_number,
                    "city": row.city if row.city else "",
                    "street": row.street if row.street else "",
                    "zip_code": row.zip_code if row.zip_code else "",
                    "percent": row.percent
                }
            return None
        except Exception as e:
            print(f"❌ Помилка отримання клієнта за номером картки: {e}")
            return None
        finally:
            conn.close()

    def update_customer(self, card_number, cust_data):
        """
        Оновлює анкетні дані клієнта.
        """
        sql_query = """
            UPDATE Customer_Card SET 
                cust_surname = ?, cust_name = ?, cust_patronymic = ?, 
                phone_number = ?, city = ?, street = ?, zip_code = ?, [percent] = ?
            WHERE card_number = ?
        """
        conn = self.db.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (
                cust_data['surname'],
                cust_data['name'],
                cust_data['patronymic'] if cust_data['patronymic'].strip() != "" else "—",
                cust_data['phone'],
                cust_data['city'] if cust_data['city'].strip() != "" else "—",
                cust_data['street'] if cust_data['street'].strip() != "" else "—",
                cust_data['zip_code'] if cust_data['zip_code'].strip() != "" else "—",
                cust_data['percent'],
                card_number
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Помилка оновлення даних клієнта: {e}")
            return False
        finally:
            conn.close()

    def delete_customer(self, card_number):
        sql_query = "DELETE FROM Customer_Card WHERE card_number = ?"
        conn = self.db.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (card_number,))
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Помилка видалення картки клієнта: {e}")
            return False
        finally:
            conn.close()