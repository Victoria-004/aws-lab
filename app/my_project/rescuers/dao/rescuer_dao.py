from app.my_project.utils.database_connection import get_db_connection
from app.my_project.rescuers.domain.rescuer import Rescuer

class RescuerDao:

    def find_by_call_id(self, call_id):
        rescuers_list = []
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT r.* FROM rescuers r
        JOIN callparticipation cp ON r.rescuers_id = cp.rescuers_id
        WHERE cp.call_id = %s
        """

        cursor.execute(query, (call_id,))

        for row in cursor.fetchall():
            rescuers_list.append(Rescuer(**row))

        cursor.close()
        conn.close()
        return rescuers_list