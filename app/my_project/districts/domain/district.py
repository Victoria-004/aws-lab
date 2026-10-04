class District:
    def __init__(self, **row):
        self.district_id = row.get('district_id')
        self.district_name = row.get('district_name')
        self.city_id = row.get('city_id')

    def to_dict(self):
        return {
            "district_id": self.district_id,
            "district_name": self.district_name,
            "city_id": self.city_id
        }