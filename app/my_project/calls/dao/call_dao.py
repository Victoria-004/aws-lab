from app.my_project.utils.database_connection import get_db_connection
from app.my_project.calls.domain.call import Call


class CallDao:
    def find_by_id(self, call_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM calls WHERE call_id = %s"
        cursor.execute(query, (call_id,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row:
            return Call(**row)
        return None