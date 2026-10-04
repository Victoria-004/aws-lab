from flask import Blueprint, Response, jsonify
import json
from app.my_project.calls.service.call_service import CallService

calls_bp = Blueprint('calls_bp', __name__, url_prefix='/calls')
call_service = CallService()


@calls_bp.route('/<int:call_id>/rescuers', methods=['GET'])
def get_rescuers_for_call(call_id):
    data = call_service.get_call_with_rescuers(call_id)

    if data:
        response_json = json.dumps(data, ensure_ascii=False)
        return Response(response_json, content_type='application/json; charset=utf-8')

    return jsonify({"error": "Call not found"}), 404