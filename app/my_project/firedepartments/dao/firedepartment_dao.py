from app.my_project.utils.database_connection import get_db_connection
from app.my_project.firedepartments.domain.firedepartment import Firedepartment


class FiredepartmentDao:

    def find_by_district_id(self, district_id):
        departments_list = []
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM firedepartments WHERE district_id = %s"

        cursor.execute(query, (district_id,))

        for row in cursor.fetchall():
            department = Firedepartment(**row)
            departments_list.append(department)

        cursor.close()
        conn.close()
        return departments_list