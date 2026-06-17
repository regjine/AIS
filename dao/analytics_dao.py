from database.connections import DatabaseConnection

class AnalyticsDAO:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_categories_by_promo_quantity(self, min_quantity):
        """
        Параметричний запит із групуванням.
        Повертає назви категорій та суму акційних товарів, 
        де ця сума більша за вказаний параметр.
        """
        sql_query = """
            SELECT Category.category_name, 
                   Sum(Store_Product.products_number) AS total_prom 
            FROM (Category  
            INNER JOIN Product ON Category.category_number = Product.category_number) 
            INNER JOIN Store_Product ON Product.id_product = Store_Product.id_product 
            WHERE Store_Product.promotional_product = True 
            GROUP BY Category.category_name 
            HAVING Sum(Store_Product.products_number) > ?
        """
        conn = self.db.get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            #take parameter
            cursor.execute(sql_query, (int(min_quantity),))
            rows = cursor.fetchall()
            
            return [
                {
                    "category_name": row.category_name, 
                    "total_prom": row.total_prom
                } 
                for row in rows
            ]
        except Exception as e:
            print(f"❌ Помилка виконання аналітичного запиту з групуванням: {e}")
            return []
        finally:
            conn.close()

    def get_absolute_promo_buyers(self):
        """
        Багатотабличний запит із подвійним запереченням (реляційне ділення).
        Знаходить покупців, які купили абсолютно всі акційні товари.
        """
        sql_query = """
            SELECT 
                Customer_Card.card_number, 
                Customer_Card.cust_surname, 
                Customer_Card.cust_name 
            FROM Customer_Card 
            WHERE NOT EXISTS ( 
                SELECT * FROM Store_Product 
                WHERE Store_Product.promotional_product = True 
                AND NOT EXISTS ( 
                    SELECT * FROM [Check] 
                    INNER JOIN Sale ON [Check].check_number = Sale.check_number 
                    WHERE [Check].card_number = Customer_Card.card_number 
                    AND Sale.UPC = Store_Product.UPC 
                ) 
            )
        """
        conn = self.db.get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            
            return [
                {
                    "card_number": row.card_number,
                    "cust_surname": row.cust_surname,
                    "cust_name": row.cust_name
                }
                for row in rows
            ]
        except Exception as e:
            print(f"❌ Помилка виконання запиту з подвійним запереченням: {e}")
            return []
        finally:
            conn.close()