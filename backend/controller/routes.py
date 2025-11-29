from flask import request
from flask_restful import Resource
from datetime import date, timedelta
from controller.models import Department, Doctor, Availability, User
from controller.database import db
from sqlalchemy import or_

def serialize_department(dep):
    return {
        "id": dep.id,
        "name": dep.name,
        "description": getattr(dep, "description", None),
        "doctors_registered": getattr(dep, "doctors_registered", 0)
    }

def serialize_doctor(d):
    user = d.user
    return {
        "id": d.id,
        "name": user.name if user else None,
        "email": user.email if user else None,
        "specialization": d.specialization,
        "experience_years": d.experience_years,
        "department": d.department.name if d.department else None,
        "department_id": d.department_id,
        "is_approved": bool(d.is_approved)
    }

def serialize_availability_slot(slot):
    return {
        "id": slot.id,
        "date": slot.date.isoformat(),
        "start_time": slot.start_time.strftime("%H:%M"),
        "end_time": slot.end_time.strftime("%H:%M"),
        "is_available": bool(slot.is_available)
    }

class DepartmentsList(Resource):
    def get(self):
        deps = Department.query.order_by(Department.name.asc()).all()
        return {"departments": [serialize_department(d) for d in deps]}, 200

class DepartmentResource(Resource):
    def get(self, department_id):
        d = Department.query.get_or_404(department_id)
        return serialize_department(d), 200

class DoctorsList(Resource):
    def get(self):
        q = (request.args.get("q") or "").strip()
        department_id = request.args.get("department_id")
        approved = request.args.get("approved")

        query = Doctor.query.join(User).filter(User.is_active == True)

        if q:
            like = f"%{q}%"
            query = query.filter(
                or_(
                    User.name.ilike(like),
                    Doctor.specialization.ilike(like)
                )
            )

        if department_id:
            try:
                did = int(department_id)
                query = query.filter(Doctor.department_id == did)
            except ValueError:
                pass

        if approved in ("0", "1"):
            query = query.filter(Doctor.is_approved == (approved == "1"))

        docs = query.order_by(Doctor.id.asc()).all()
        return {"doctors": [serialize_doctor(d) for d in docs]}, 200

class DoctorRes(Resource):
    def get(self, doctor_id):
        d = Doctor.query.get_or_404(doctor_id)
        profile = serialize_doctor(d)

        today = date.today()
        end = today + timedelta(days=6)
        slots = Availability.query.filter(
            Availability.doctor_id == d.id,
            Availability.date >= today,
            Availability.date <= end
        ).order_by(Availability.date.asc(), Availability.start_time.asc()).all()

        profile["availability"] = [serialize_availability_slot(s) for s in slots]
        return profile, 200