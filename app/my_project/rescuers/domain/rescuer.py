class Rescuer:
    def __init__(self, **row):
        self.rescuers_id = row.get('rescuers_id')
        self.first_name = row.get('first_name')
        self.last_name = row.get('last_name')
        self.fire_department_id = row.get('fire_department_id')
        self.rang = row.get('rang')

    def to_dict(self):
        return {
            "rescuers_id": self.rescuers_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "fire_department_id": self.fire_department_id,
            "rang": self.rang
        }