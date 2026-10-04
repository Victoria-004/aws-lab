from app.my_project.rescuers.dao.rescuer_dao import RescuerDao

class RescuerService:
    def __init__(self):
        self.rescuer_dao = RescuerDao()

    def get_rescuers_by_call_id(self, call_id):
        rescuers = self.rescuer_dao.find_by_call_id(call_id)
        return [r.to_dict() for r in rescuers]