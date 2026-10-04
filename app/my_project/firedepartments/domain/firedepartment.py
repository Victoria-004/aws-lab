class Firedepartment:
    def __init__(self, **row):
        self.fire_department_id = row.get('fire_department_id')
        self.fire_department_name = row.get('fire_department_name')
        self.district_id = row.get('district_id')
        self.adress = row.get('adress')

    def to_dict(self):
        return {
            "fire_department_id": self.fire_department_id,
            "fire_department_name": self.fire_department_name,
            "district_id": self.district_id,
            "adress": self.adress
        }