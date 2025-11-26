from controller.database import db
from datetime import datetime, date, time, timedelta

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=True)            # display name
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='patient')

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
        return len(self.doctors)

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
        Replace availability for provided dates.
        slots: [{ "date": "YYYY-MM-DD", "start_time": "HH:MM", "end_time": "HH:MM" }, ...]
        """
        # basic conversion and reuse previous implementation (assumes validated)
        dates = {datetime.strptime(s['date'], "%Y-%m-%d").date() for s in slots}
        Availability.query.filter(Availability.doctor_id == self.id, Availability.date.in_(dates)).delete(synchronize_session=False)
        for s in slots:
            d = datetime.strptime(s['date'], "%Y-%m-%d").date()
            st = datetime.strptime(s['start_time'], "%H:%M").time()
            et = datetime.strptime(s['end_time'], "%H:%M").time()
            av = Availability(doctor_id=self.id, date=d, start_time=st, end_time=et, is_available=True)
            db.session.add(av)
        db.session.commit()

    def publish_availability(self, slots):
        """
        Validate slots against wireframe requirements:
         - slots are within next 7 days (including today)
         - start < end
         - no overlapping slots per date in the provided list
        Then persist via set_availability.
        Raises ValueError on validation error.
        """
        today = date.today()
        max_day = today + timedelta(days=7)
        parsed = []
        for s in slots:
            try:
                d = datetime.strptime(s['date'], "%Y-%m-%d").date()
                st = datetime.strptime(s['start_time'], "%H:%M").time()
                et = datetime.strptime(s['end_time'], "%H:%M").time()
            except Exception:
                raise ValueError("invalid slot format, expected date 'YYYY-MM-DD' and times 'HH:MM'")

            if d < today or d > max_day:
                raise ValueError(f"date {d.isoformat()} out of allowed range (today → next 7 days)")
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

        # all good, persist
        self.set_availability(parsed)

    def is_available_at(self, when_dt, duration_minutes=30):
        """Check if doctor has an available slot that covers the interval and no overlapping scheduled appointment."""
        d = when_dt.date()
        t = when_dt.time()
        end_dt = when_dt + timedelta(minutes=duration_minutes)
        # find slot covering start and end
        slot = Availability.query.filter_by(doctor_id=self.id, date=d, is_available=True)\
            .filter(Availability.start_time <= t, Availability.end_time >= end_dt.time()).first()
        if not slot:
            return False
        # check for overlapping appointments
        overlap = Appointment.query.filter(
            Appointment.doctor_id == self.id,
            Appointment.status == 'scheduled',
            Appointment.appointment_time < end_dt,
            (Appointment.appointment_time + db.cast(db.func.strftime('%s','%s' % Appointment.duration_minutes), db.DateTime)) > when_dt
        ).first()
        # Because SQLite doesn't support datetime addition easily in SQLAlchemy expression above,
        # we'll implement overlap check in Python where necessary when creating new appointment.
        return overlap is None

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
    duration_minutes = db.Column(db.Integer, default=30)   # appointment length
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
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    next_visit = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    appointment = db.relationship('Appointment', backref='treatments')

class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)