from flask import Blueprint, jsonify, request, Response
import json
from app.my_project.districts.service.district_service import DistrictService
from app.my_project.firedepartments.service.firedepartment_service import FiredepartmentService

districts_bp = Blueprint('districts_bp', __name__, url_prefix='/districts')

service = DistrictService()
firedep_service = FiredepartmentService()

@districts_bp.route('', methods=['GET'])
def get_all_districts():
    all_districts = service.get_all_districts()
    response_json = json.dumps(all_districts, ensure_ascii=False)
    return Response(response_json, content_type='application/json; charset=utf-8')

@districts_bp.route('/<int:district_id>', methods=['GET'])
def get_district_by_id(district_id):
    district = service.get_district_by_id(district_id)
    if district:
        response_json = json.dumps(district, ensure_ascii=False)
        return Response(response_json, content_type='application/json; charset=utf-8')
    return jsonify({"error": "District not found"}), 404

@districts_bp.route('', methods=['POST'])
def create_district():
    data = request.get_json()
    new_district = service.create_district(data)
    response_json = json.dumps(new_district, ensure_ascii=False)
    return Response(response_json, content_type='application/json; charset=utf-8'), 201

@districts_bp.route('/<int:district_id>', methods=['PUT'])
def update_district(district_id):
    data = request.get_json()
    updated_district = service.update_district(district_id, data)
    if updated_district:
        response_json = json.dumps(updated_district, ensure_ascii=False)
        return Response(response_json, content_type='application/json; charset=utf-8')
    return jsonify({"error": "District not found"}), 404

@districts_bp.route('/<int:district_id>', methods=['DELETE'])
def delete_district(district_id):
    service.delete_district(district_id)
    return jsonify({"message": "District deleted successfully"}), 200

@districts_bp.route('/<int:district_id>/firedepartments', methods=['GET'])
def get_all_firedepartments_for_district(district_id):
    district = service.get_district_by_id(district_id)
    if not district:
        return jsonify({"error": "District not found"}), 404

    departments = firedep_service.get_firedepartments_by_district(district_id)

    response_json = json.dumps(departments, ensure_ascii=False)
    return Response(response_json, content_type='application/json; charset=utf-8')