from app.my_project.calls.dao.call_dao import CallDao
from app.my_project.rescuers.dao.rescuer_dao import RescuerDao


class CallService:
    def __init__(self):
        self.call_dao = CallDao()
        self.rescuer_dao = RescuerDao()

    def get_call_with_rescuers(self, call_id):
        call = self.call_dao.find_by_id(call_id)

        if not call:
            return None

        rescuers = self.rescuer_dao.find_by_call_id(call_id)

        return {
            "call_details": call.to_dict(),
            "rescuers_list": [r.to_dict() for r in rescuers]
        }