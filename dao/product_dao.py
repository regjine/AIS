from database.connections import DatabaseConnection

class ProductDAO:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_products(self):
        """
        Gets a list of all products from the database, sorted alphabetically by name.
        """
        sql_query = """
            SELECT p.id_product, p.product_name, p.characteristics, 
                   p.category_number, c.category_name
            FROM Product p
            INNER JOIN Category c ON p.category_number = c.category_number
            ORDER BY p.product_name ASC
        """
        
        conn = self.db.get_connection()
        if not conn:
            return []
            
        products_list = []
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            
            for row in rows:
                products_list.append({
                    "id": row.id_product,
                    "name": row.product_name,
                    "characteristics": row.characteristics,
                    "category_id": row.category_number,
                    "category_name": row.category_name
                })
            return products_list
        except Exception as e:
            print(f"❌ Exception while fetching all products (get_all_products): {e}")
            return []
        finally:
            conn.close()

    def add_product(self, prod_data):
        """
        Adds a new product to the database. Returns True if successful, False otherwise.
        """
        sql_query = """
            INSERT INTO Product (id_product, category_number, product_name, characteristics)
            VALUES (?, ?, ?, ?)
        """
        conn = self.db.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (
                prod_data['id'],
                prod_data['category_number'],
                prod_data['name'],
                prod_data['characteristics']
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Exception while adding product: {e}")
            return False
        finally:
            conn.close()

    def get_product_by_id(self, product_id):
        """
        Gets data of a product by its ID. Returns a dictionary with product details if found, None otherwise.
        """
        sql_query = "SELECT id_product, category_number, product_name, characteristics FROM Product WHERE id_product = ?"
        conn = self.db.get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (product_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row.id_product,
                    "category_number": row.category_number,
                    "name": row.product_name,
                    "characteristics": row.characteristics
                }
            return None
        except Exception as e:
            print(f"❌ Exception while fetching product by ID {product_id}: {e}")
            return None
        finally:
            conn.close()

    def update_product(self, product_id, prod_data):
        """
        Updates the data of a product in the database. Returns True if successful, False otherwise.
        """
        sql_query = """
            UPDATE Product SET 
                category_number = ?, product_name = ?, characteristics = ? 
            WHERE id_product = ?
        """
        conn = self.db.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (
                prod_data['category_number'],
                prod_data['name'],
                prod_data['characteristics'],
                product_id
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Exception while updating product: {e}")
            return False
        finally:
            conn.close()

    def delete_product(self, product_id):
        """
        Deletes a product from the database by its ID. Returns True if successful, False otherwise.
        """
        sql_query = "DELETE FROM Product WHERE id_product = ?"
        conn = self.db.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (product_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Exception while deleting product: {e}")
            return False
        finally:
            conn.close()