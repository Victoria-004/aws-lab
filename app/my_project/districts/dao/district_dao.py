from app.my_project.utils.database_connection import get_db_connection
from app.my_project.districts.domain.district import District

class DistrictDao:

    def find_all(self):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM districts"
        cursor.execute(query)
        result = [District(**row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return result

    def find_by_id(self, district_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM districts WHERE district_id = %s"
        cursor.execute(query, (district_id,))
        row = cursor.fetchone()
        if row:
            result = District(**row)
        else:
            result = None
        cursor.close()
        conn.close()
        return result

    def create(self, district_data):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO districts (district_name, city_id) VALUES (%s, %s)"
        cursor.execute(query, (district_data['district_name'], district_data['city_id']))
        conn.commit()
        created_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return self.find_by_id(created_id)

    def update(self, district_id, district_data):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "UPDATE districts SET district_name = %s, city_id = %s WHERE district_id = %s"
        cursor.execute(query, (district_data['district_name'], district_data['city_id'], district_id))
        conn.commit()
        cursor.close()
        conn.close()
        return self.find_by_id(district_id)

    def delete(self, district_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "DELETE FROM districts WHERE district_id = %s"
        cursor.execute(query, (district_id,))
        conn.commit()
        cursor.close()
        conn.close()