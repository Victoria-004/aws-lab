from app.my_project.districts.dao.district_dao import DistrictDao

class DistrictService:
    def __init__(self):
        self.district_dao = DistrictDao()

    def get_all_districts(self):
        districts = self.district_dao.find_all()
        return [district.to_dict() for district in districts]

    def get_district_by_id(self, district_id):
        district = self.district_dao.find_by_id(district_id)
        if district:
            return district.to_dict()
        return None

    def create_district(self, data):
        district = self.district_dao.create(data)
        return district.to_dict()

    def update_district(self, district_id, data):
        district = self.district_dao.update(district_id, data)
        if district:
            return district.to_dict()
        return None

    def delete_district(self, district_id):
        self.district_dao.delete(district_id)