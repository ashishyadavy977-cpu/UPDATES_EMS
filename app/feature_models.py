from datetime import datetime
from app.models import db


class WaitlistEntry(db.Model):
    __tablename__ = 'event_waitlist'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False, index=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), default='waiting', nullable=False)  # waiting/promoted/cancelled
    promoted_at = db.Column(db.DateTime, nullable=True)
    user = db.relationship('User', backref=db.backref('waitlist_entries', lazy=True))
    event = db.relationship('Event', backref=db.backref('waitlist_entries', lazy=True))
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='unique_waitlist_user_event'),)


class Attendance(db.Model):
    __tablename__ = 'event_attendance'
    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey('registrations.id'), unique=True, nullable=False, index=True)
    checked_in_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    checked_in_by = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)
    registration = db.relationship('Registration', backref=db.backref('attendance', uselist=False))


class Feedback(db.Model):
    __tablename__ = 'event_feedback'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user = db.relationship('User', backref=db.backref('event_feedback', lazy=True))
    event = db.relationship('Event', backref=db.backref('feedback', lazy=True))
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='unique_feedback_user_event'),)


class NotificationLog(db.Model):
    __tablename__ = 'notification_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=True, index=True)
    channel = db.Column(db.String(20), nullable=False)  # email/sms
    recipient = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=True)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # sent/failed/skipped
    error = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
