from database.connections import DatabaseConnection

class StoreProductDAO:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_store_products(self):
        """
        Gets a list of all products in the store along with their name sorted by quantity (from highest to lowest).
        """
        sql_query = """
            SELECT sp.UPC, sp.UPC_prom, sp.id_product, sp.selling_price, 
                   sp.products_number, sp.promotional_product,
                   p.product_name
            FROM Store_Product sp
            INNER JOIN Product p ON sp.id_product = p.id_product
            ORDER BY sp.products_number DESC
        """
        
        conn = self.db.get_connection()
        if not conn:
            return []
            
        store_products_list = []
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            
            for row in rows:
                store_products_list.append({
                    "upc": row.UPC,
                    "upc_prom": row.UPC_prom if row.UPC_prom else "",
                    "product_id": row.id_product,
                    "price": row.selling_price,
                    "quantity": row.products_number,
                    "is_promo": bool(row.promotional_product),
                    "product_name": row.product_name
                })
            return store_products_list
        except Exception as e:
            print(f"❌ Exception while executing SQL query (get_all_store_products): {e}")
            return []
        finally:
            conn.close()

    def add_store_product(self, sp_data):
        sql_query = """
            INSERT INTO Store_Product (UPC, UPC_prom, id_product, selling_price, products_number, promotional_product)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        conn = self.db.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (
                sp_data['upc'],
                sp_data['upc_prom'] if sp_data['upc_prom'] else None, 
                sp_data['product_id'],
                sp_data['price'],
                sp_data['quantity'],
                sp_data['is_promo']
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Exception while adding store product: {e}")
            return False
        finally:
            conn.close()
    
    def get_store_product_by_upc(self, upc):
        sql_query = """
            SELECT UPC, UPC_prom, id_product, selling_price, products_number, promotional_product 
            FROM Store_Product 
            WHERE UPC = ?
        """
        conn = self.db.get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (upc,))
            row = cursor.fetchone()
            if row:
                return {
                    "upc": row.UPC,
                    "upc_prom": row.UPC_prom if row.UPC_prom else "",
                    "product_id": row.id_product,
                    "price": row.selling_price,
                    "quantity": row.products_number,
                    "is_promo": bool(row.promotional_product)
                }
            return None
        except Exception as e:
            print(f"❌ Exception while fetching store product by UPC {upc}: {e}")
            return None
        finally:
            conn.close()

    def update_store_product(self, upc, sp_data):
        sql_query = """
            UPDATE Store_Product 
            SET UPC_prom = ?, id_product = ?, selling_price = ?, 
                products_number = ?, promotional_product = ? 
            WHERE UPC = ?
        """
        conn = self.db.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (
                sp_data['upc_prom'] if sp_data['upc_prom'] else None,
                sp_data['product_id'],
                sp_data['price'],
                sp_data['quantity'],
                sp_data['is_promo'],
                upc
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Exception while updating store product: {e}")
            return False
        finally:
            conn.close()

    def delete_store_product(self, upc):
        sql_query = "DELETE FROM Store_Product WHERE UPC = ?"
        conn = self.db.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (upc,))
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Exception while deleting store product: {e}")
            return False
        finally:
            conn.close()