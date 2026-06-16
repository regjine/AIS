from database.connections import DatabaseConnection

class CategoryDAO:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_categories(self):
        """
        Gets a list of all categories from the database, sorted alphabetically by name.
        """
        sql_query = """
            SELECT category_number, category_name 
            FROM Category 
            ORDER BY category_name ASC
        """
        
        conn = self.db.get_connection()
        if not conn:
            return []
            
        categories_list = []
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            
            for row in rows:
                categories_list.append({
                    "id": row.category_number,
                    "name": row.category_name
                })
            return categories_list
        except Exception as e:
            print(f"❌ Exception while executing SQL query (get_all_categories): {e}")
            return []
        finally:
            conn.close()
    
    def add_category(self, category_id, category_name):
        """
        Add new category. Returns True if successful, False otherwise.
        """
        sql_query = "INSERT INTO Category (category_number, category_name) VALUES (?, ?)"
        
        conn = self.db.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (category_id, category_name))
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Exception while executing SQL query (add_category): {e}")
            return False
        finally:
            conn.close()

    def get_category_by_id(self, category_id):
        """
        Gets categories name by its ID. Returns a dictionary with category details or None if not found.
        """
        sql_query = "SELECT category_number, category_name FROM Category WHERE category_number = ?"
        conn = self.db.get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (category_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row.category_number,
                    "name": row.category_name
                }
            return None
        except Exception as e:
            print(f"❌ Помилка отримання категорії за ID {category_id}: {e}")
            return None
        finally:
            conn.close()

    def update_category(self, category_id, new_name):
        """
        Updates the name of a category in the database.
        """
        sql_query = "UPDATE Category SET category_name = ? WHERE category_number = ?"
        conn = self.db.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (new_name, category_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Помилка оновлення категорії: {e}")
            return False
        finally:
            conn.close()

    def delete_category(self, category_id):
        """
        Deletes a category from the database by its ID.
        """
        sql_query = "DELETE FROM Category WHERE category_number = ?"
        conn = self.db.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (category_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Помилка видалення категорії: {e}")
            return False
        finally:
            conn.close()