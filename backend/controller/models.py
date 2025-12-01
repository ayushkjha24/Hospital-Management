from controller.database import db
from datetime import datetime, date, time, timedelta
from sqlalchemy import event

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=True)            # display name
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='patient')
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # backrefs:
    doctor = db.relationship('Doctor', uselist=False, back_populates='user')
    patient = db.relationship('Patient', uselist=False, back_populates='user')

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    # relationship for convenience
    doctors = db.relationship('Doctor', back_populates='department')

    @property
    def doctors_registered(self):
        return len(self.doctors or [])

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    experience_years = db.Column(db.Integer, nullable=False, default=0)
    is_approved = db.Column(db.Boolean, default=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)

    user = db.relationship('User', back_populates='doctor')
    department = db.relationship('Department', back_populates='doctors')
    availabilities = db.relationship('Availability', backref='doctor', cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', backref='doctor', cascade='all, delete-orphan')

    def set_availability(self, slots):
        """
        Persist availability slots. slots: [{ "date": "YYYY-MM-DD", "start_time":"HH:MM", "end_time":"HH:MM" }, ...]
        Replaces availability rows for the provided dates. Will raise ValueError if any existing scheduled appointments
        for those dates would fall outside new availability (prevents orphaning appointments).
        """
        if not slots:
            return

        # convert to date -> list of (start_time, end_time)
        ranges_by_date = {}
        for s in slots:
            d = datetime.strptime(s['date'], "%Y-%m-%d").date()
            st = datetime.strptime(s['start_time'], "%H:%M").time()
            et = datetime.strptime(s['end_time'], "%H:%M").time()
            ranges_by_date.setdefault(d, []).append((st, et))

        # check for appointment conflicts on each date
        for d, ranges in ranges_by_date.items():
            # gather scheduled appointments for this doctor on date d
            start_of_day = datetime.combine(d, time.min)
            end_of_day = datetime.combine(d, time.max)
            appts = Appointment.query.filter(
                Appointment.doctor_id == self.id,
                Appointment.status == 'scheduled',
                Appointment.appointment_time >= start_of_day,
                Appointment.appointment_time <= end_of_day
            ).all()
            for a in appts:
                a_start = a.appointment_time.time()
                a_end = (a.appointment_time + timedelta(minutes=a.duration_minutes or 30)).time()
                covered = False
                for (st, et) in ranges:
                    # appointment interval must be fully inside some new slot
                    if (a_start >= st) and (a_end <= et):
                        covered = True
                        break
                if not covered:
                    raise ValueError(f"Appointment {a.id} at {a.appointment_time.isoformat()} would be outside new availability for {d.isoformat()}")

        # delete existing availability rows for these dates, then insert new slots
        dates = list(ranges_by_date.keys())
        if dates:
            Availability.query.filter(Availability.doctor_id == self.id, Availability.date.in_(dates)).delete(synchronize_session=False)
        for d, ranges in ranges_by_date.items():
            for st, et in ranges:
                av = Availability(doctor_id=self.id, date=d, start_time=st, end_time=et, is_available=True)
                db.session.add(av)
        db.session.commit()

    def publish_availability(self, slots):
        """
        Validate and persist slots for next 7 days.
        Raises ValueError on validation error.
        """
        today = date.today()
        max_day = today + timedelta(days=6)  # next 7 days inclusive
        parsed = []
        for s in slots:
            try:
                d = datetime.strptime(s['date'], "%Y-%m-%d").date()
                st = datetime.strptime(s['start_time'], "%H:%M").time()
                et = datetime.strptime(s['end_time'], "%H:%M").time()
            except Exception:
                raise ValueError("invalid slot format, expected date 'YYYY-MM-DD' and times 'HH:MM'")

            if d < today or d > max_day:
                raise ValueError(f"date {d.isoformat()} out of allowed range (next 7 days)")
            if st >= et:
                raise ValueError("start_time must be before end_time")
            parsed.append({'date': d.isoformat(), 'start_time': st.strftime("%H:%M"), 'end_time': et.strftime("%H:%M")})

        # intra-day overlap check
        slots_by_date = {}
        for p in parsed:
            slots_by_date.setdefault(p['date'], []).append(p)
        for d, items in slots_by_date.items():
            items_sorted = sorted(items, key=lambda x: x['start_time'])
            for i in range(1, len(items_sorted)):
                if items_sorted[i]['start_time'] < items_sorted[i-1]['end_time']:
                    raise ValueError(f"overlapping slots for date {d}")

        # call set_availability which will also check appointment conflicts
        self.set_availability(parsed)

    def is_available_at(self, when_dt, duration_minutes=30):
        """Return True if an available slot exists that covers the whole interval and no overlapping appointment exists."""
        d = when_dt.date()
        t_start = when_dt.time()
        t_end = (when_dt + timedelta(minutes=duration_minutes)).time()
        slot = Availability.query.filter_by(doctor_id=self.id, date=d, is_available=True)\
            .filter(Availability.start_time <= t_start, Availability.end_time >= t_end).first()
        if not slot:
            return False
        # check overlapping scheduled appointments (simple python check)
        appts = Appointment.query.filter_by(doctor_id=self.id, status='scheduled').all()
        for a in appts:
            a_start = a.appointment_time
            a_end = a_start + timedelta(minutes=a.duration_minutes or 30)
            if not (a_end <= when_dt or a_start >= when_dt + timedelta(minutes=duration_minutes)):
                return False
        return True

class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    medical_history = db.Column(db.Text)
    user = db.relationship('User', back_populates='patient')
    appointments = db.relationship('Appointment', backref='patient', cascade='all, delete-orphan')

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_time = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)
    status = db.Column(db.String(50), default='scheduled')  # scheduled, completed, cancelled
    reason = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def overlaps(self, start_dt, end_dt):
        """Return True if this appointment overlaps given interval."""
        appt_start = self.appointment_time
        appt_end = self.appointment_time + timedelta(minutes=self.duration_minutes or 30)
        return not (appt_end <= start_dt or appt_start >= end_dt)

class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    diagnosis = db.Column(db.Text)
    test_done = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    next_visit = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    appointment = db.relationship('Appointment', backref='treatments')

class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Create a Patient row automatically after a User is inserted if role == 'patient'
def _create_patient_after_insert(mapper, connection, target):
    if getattr(target, "role", None) == "patient":
        connection.execute(
            Patient.__table__.insert().values(user_id=target.id, medical_history=None)
        )

event.listen(User, "after_insert", _create_patient_after_insert)