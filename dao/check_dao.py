from database.connections import DatabaseConnection

class CheckDAO:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_checks(self):
        sql_query = """
            SELECT c.check_number, c.id_employee, c.card_number, 
                   c.print_date, c.sum_total, c.vat,
                   e.empl_surname, e.empl_name
            FROM [Check] c
            INNER JOIN Employee e ON c.id_employee = e.id_employee
            ORDER BY c.print_date DESC
        """
        
        conn = self.db.get_connection()
        if not conn:
            return []
            
        checks_list = []
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            
            for row in rows:
                checks_list.append({
                    "check_number": row.check_number,
                    "id_employee": row.id_employee,
                    "cashier_name": f"{row.empl_surname} {row.empl_name[0]}.",
                    "card_number": row.card_number if row.card_number else "—",
                    "print_date": row.print_date,
                    "sum_total": row.sum_total,
                    "vat": row.vat
                })
            return checks_list
        except Exception as e:
            print(f"❌ Помилка виконання SQL-запиту (get_all_checks): {e}")
            return []
        finally:
            conn.close()

    def create_check_with_sales(self, check_data, sales_list):
        """
        Створює головний запис чека в таблиці [Check] та 
        усі пов'язані з ним товари в таблиці [Sale].
        """
        insert_check_sql = """
            INSERT INTO [Check] (check_number, id_employee, card_number, print_date, sum_total, vat)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        insert_sale_sql = """
            INSERT INTO Sale (UPC, check_number, product_number, selling_price)
            VALUES (?, ?, ?, ?)
        """
        update_stock_sql = """
            UPDATE Store_Product 
            SET products_number = products_number - ? 
            WHERE UPC = ?
        """

        conn = self.db.get_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            
            #Вставляємо головний запис чека
            cursor.execute(insert_check_sql, (
                check_data['check_number'],
                check_data['id_employee'],
                check_data['card_number'] if check_data['card_number'] else None,
                check_data['print_date'],
                check_data['sum_total'],
                check_data['vat']
            ))
            
            #Вставляємо кожну позицію товару з чека та оновлюємо залишки
            for sale in sales_list:
                cursor.execute(insert_sale_sql, (
                    sale['upc'],
                    check_data['check_number'],
                    sale['quantity'],
                    sale['price']
                ))
                
                #Списуємо товар з полиці супермаркету
                cursor.execute(update_stock_sql, (sale['quantity'], sale['upc']))
                
            conn.commit() #Фіксуємо транзакцію, якщо все пройшло без помилок
            return True
        except Exception as e:
            conn.rollback() #Скасовуємо все, якщо хоч один товар не вставився або виник збій
            print(f"❌ Помилка створення чека та продажів: {e}")
            return False
        finally:
            conn.close()       

    def delete_check(self, check_number):
        """
        Скасовує чек: повертає товари на склад супермаркету 
        та видаляє чек разом із позиціями продажів.
        """
        #find all sales associated with the check
        select_sales_sql = "SELECT UPC, product_number FROM Sale WHERE check_number = ?"
        
        #return products back to stock
        return_stock_sql = "UPDATE Store_Product SET products_number = products_number + ? WHERE UPC = ?"
        
        delete_sales_sql = "DELETE FROM Sale WHERE check_number = ?"
        delete_check_sql = "DELETE FROM [Check] WHERE check_number = ?"

        conn = self.db.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            
            cursor.execute(select_sales_sql, (check_number,))
            items = cursor.fetchall()
            
            #return products back to stock
            for item in items:
                cursor.execute(return_stock_sql, (item.product_number, item.UPC))
                
            #delete sales and check records
            cursor.execute(delete_sales_sql, (check_number,))
            cursor.execute(delete_check_sql, (check_number,))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"❌ Помилка під час скасування та видалення чека: {e}")
            return False
        finally:
            conn.close() 

    def get_check_by_number(self, check_number):
        sql_query = """
            SELECT c.check_number, c.print_date, c.sum_total, c.vat, c.card_number,
                   e.empl_surname, e.empl_name
            FROM [Check] c
            INNER JOIN Employee e ON c.id_employee = e.id_employee
            WHERE c.check_number = ?
        """
        conn = self.db.get_connection()
        if not conn: return None
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (check_number,))
            row = cursor.fetchone()
            if row:
                return {
                    "check_number": row.check_number,
                    "print_date": row.print_date,
                    "sum_total": row.sum_total,
                    "vat": row.vat,
                    "card_number": row.card_number if row.card_number else "—",
                    "cashier_name": f"{row.empl_surname} {row.empl_name[0]}."
                }
            return None
        except Exception as e:
            print(f"❌ Помилка отримання чека за номером: {e}")
            return None
        finally:
            conn.close()

    def get_check_details(self, check_number):
        sql_query = """
            SELECT s.UPC, s.product_number, s.selling_price, p.product_name
            FROM (Sale s
            INNER JOIN Store_Product sp ON s.UPC = sp.UPC)
            INNER JOIN Product p ON sp.id_product = p.id_product
            WHERE s.check_number = ?
        """
        conn = self.db.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (check_number,))
            rows = cursor.fetchall()
            return [{
                "upc": row.UPC,
                "quantity": row.product_number,
                "price": row.selling_price,
                "total_item_price": row.product_number * row.selling_price,
                "product_name": row.product_name
            } for row in rows]
        except Exception as e:
            print(f"❌ Помилка отримання деталей чека {check_number}: {e}")
            return []
        finally:
            conn.close()