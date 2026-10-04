from app.my_project.firedepartments.dao.firedepartment_dao import FiredepartmentDao


class FiredepartmentService:
    def __init__(self):
        self.firedepartment_dao = FiredepartmentDao()

    def get_firedepartments_by_district(self, district_id):
        departments = self.firedepartment_dao.find_by_district_id(district_id)

        return [dept.to_dict() for dept in departments]