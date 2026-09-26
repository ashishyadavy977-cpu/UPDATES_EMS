from datetime import datetime, timedelta
import csv
import io
import re
from functools import wraps
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from app.models import db, Event, Registration, User, Admin
from app.feature_models import WaitlistEntry, Attendance, Feedback, NotificationLog
from app.utils import generate_qr_code
from app.services import notify_user

features_bp = Blueprint('features', __name__)


def user_only(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, User):
            return jsonify({'success': False, 'message': 'User login required'}), 401
        return f(*args, **kwargs)
    return wrapped


def admin_only(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Admin):
            flash('Admin access required', 'danger')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return wrapped


def event_status(event):
    now = datetime.now()
    start = datetime.combine(event.event_date, event.event_time)
    end = start + timedelta(hours=3)
    if now < start:
        return 'upcoming'
    if start <= now <= end:
        return 'live'
    return 'completed'


@features_bp.get('/features/event/<int:event_id>/status')
@login_required
@user_only
def event_status_api(event_id):
    event = Event.query.get_or_404(event_id)
    return jsonify({'success': True, 'status': event_status(event), 'event': event.event_name,
                    'remaining_seats': event.remaining_seats})


@features_bp.get('/features/event/<int:event_id>/calendar.ics')
@login_required
def calendar_event(event_id):
    event = Event.query.get_or_404(event_id)
    start = datetime.combine(event.event_date, event.event_time)
    end = start + timedelta(hours=3)
    def esc(value):
        return re.sub(r'([,;\\])', r'\\\1', str(value or '')).replace('\n', '\\n')
    body = "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//EMS//Event Management System//EN\r\n"
    body += "BEGIN:VEVENT\r\n"
    body += f"UID:ems-event-{event.id}@localhost\r\nDTSTAMP:{datetime.utcnow():%Y%m%dT%H%M%SZ}\r\n"
    body += f"DTSTART:{start:%Y%m%dT%H%M%S}\r\nDTEND:{end:%Y%m%dT%H%M%S}\r\n"
    body += f"SUMMARY:{esc(event.event_name)}\r\nLOCATION:{esc(event.venue)}\r\nDESCRIPTION:{esc(event.description)}\r\n"
    body += "END:VEVENT\r\nEND:VCALENDAR\r\n"
    return Response(body, mimetype='text/calendar', headers={
        'Content-Disposition': f'attachment; filename="event_{event.id}.ics"'
    })


@features_bp.post('/features/event/<int:event_id>/feedback')
@user_only
@login_required
def feedback(event_id):
    event = Event.query.get_or_404(event_id)
    registration = Registration.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if not registration:
        return jsonify({'success': False, 'message': 'Register for the event before submitting feedback'}), 400
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '').strip()
    if rating not in range(1, 6):
        return jsonify({'success': False, 'message': 'Rating must be between 1 and 5'}), 400
    item = Feedback.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if item:
        item.rating, item.comment = rating, comment
    else:
        db.session.add(Feedback(user_id=current_user.id, event_id=event_id, rating=rating, comment=comment))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Feedback saved successfully'})


@features_bp.post('/features/checkin')
@admin_only
def checkin():
    payload = request.get_json(silent=True) or request.form
    raw = str(payload.get('qr_data', '')).strip()
    reg_id = payload.get('registration_id', type=int) if hasattr(payload, 'get') else None
    if not reg_id and raw:
        match = re.match(r'^REG_(\d+)_', raw)
        if match:
            reg_id = int(match.group(1))
        elif raw.isdigit():
            reg_id = int(raw)
    if not reg_id:
        return jsonify({'success': False, 'message': 'Invalid QR code'}), 400
    registration = Registration.query.get(reg_id)
    if not registration:
        return jsonify({'success': False, 'message': 'Registration not found'}), 404
    existing = Attendance.query.filter_by(registration_id=registration.id).first()
    if existing:
        return jsonify({'success': True, 'already_checked_in': True,
                        'message': f"Already checked in: {registration.user.name}",
                        'checked_in_at': existing.checked_in_at.isoformat()})
    attendance = Attendance(registration_id=registration.id, checked_in_by=current_user.id)
    db.session.add(attendance)
    db.session.commit()
    return jsonify({'success': True, 'message': f"Check-in successful for {registration.user.name}",
                    'user': registration.user.name, 'event': registration.event.event_name,
                    'checked_in_at': attendance.checked_in_at.isoformat()})


@features_bp.get('/admin/features/checkin')
@admin_only
def checkin_page():
    return render_template('admin/checkin.html')


@features_bp.get('/admin/features/analytics')
@admin_only
def analytics():
    events = Event.query.order_by(Event.event_date.desc()).all()
    event_rows = []
    for event in events:
        reg_count = Registration.query.filter_by(event_id=event.id).count()
        wait_count = WaitlistEntry.query.filter_by(event_id=event.id, status='waiting').count()
        attendance_count = (db.session.query(Attendance).join(Registration)
                            .filter(Registration.event_id == event.id).count())
        feedback_rows = Feedback.query.filter_by(event_id=event.id).all()
        avg_rating = round(sum(x.rating for x in feedback_rows) / len(feedback_rows), 2) if feedback_rows else 0
        event_rows.append({'event': event, 'registrations': reg_count, 'waitlist': wait_count,
                           'attendance': attendance_count, 'avg_rating': avg_rating})
    total_attendance = Attendance.query.count()
    total_waitlist = WaitlistEntry.query.filter_by(status='waiting').count()
    total_feedback = Feedback.query.count()
    return render_template('admin/feature_analytics.html', event_rows=event_rows,
                           total_attendance=total_attendance, total_waitlist=total_waitlist,
                           total_feedback=total_feedback)


@features_bp.get('/admin/features/attendance.csv')
@admin_only
def attendance_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Registration ID', 'User', 'Email', 'Event', 'Event Date', 'Checked In At'])
    rows = Attendance.query.join(Registration).all()
    for item in rows:
        reg = item.registration
        writer.writerow([reg.id, reg.user.name, reg.user.email, reg.event.event_name,
                         reg.event.event_date.isoformat(), item.checked_in_at.strftime('%Y-%m-%d %H:%M:%S')])
    return Response(output.getvalue(), mimetype='text/csv', headers={
        'Content-Disposition': 'attachment; filename="attendance_report.csv"'
    })


@features_bp.post('/admin/features/notify/<int:event_id>')
@admin_only
def notify_event(event_id):
    event = Event.query.get_or_404(event_id)
    subject = request.form.get('subject', f'Update: {event.event_name}').strip()
    message = request.form.get('message', '').strip()
    if not message:
        flash('Notification message is required.', 'danger')
        return redirect(url_for('features.analytics'))
    registrations = Registration.query.filter_by(event_id=event.id).all()
    for registration in registrations:
        notify_user(registration.user, subject, message, event.id)
    db.session.commit()
    flash(f'Notification queued for {len(registrations)} registered attendee(s).', 'success')
    return redirect(url_for('features.analytics'))


def promote_waitlisted(event):
    if event.is_full:
        return None
    candidate = (WaitlistEntry.query.filter_by(event_id=event.id, status='waiting')
                 .order_by(WaitlistEntry.joined_at.asc()).first())
    if not candidate:
        return None
    registration = Registration(user_id=candidate.user_id, event_id=event.id)
    db.session.add(registration)
    db.session.flush()
    registration.qr_code_filename = generate_qr_code(registration.id, candidate.user.email, event.event_name)
    candidate.status = 'promoted'
    candidate.promoted_at = datetime.utcnow()
    notify_user(candidate.user, f'You are confirmed for {event.event_name}',
                f'Good news! A seat is available for {event.event_name} on {event.event_date} at {event.event_time}.', event.id)
    return registration


@features_bp.post('/features/waitlist/<int:event_id>')
@user_only
@login_required
def join_waitlist(event_id):
    event = Event.query.get_or_404(event_id)
    if not event.is_full:
        return jsonify({'success': False, 'message': 'Seats are available. Register directly.'}), 400
    if Registration.query.filter_by(user_id=current_user.id, event_id=event.id).first():
        return jsonify({'success': False, 'message': 'You are already registered.'}), 400
    existing = WaitlistEntry.query.filter_by(user_id=current_user.id, event_id=event.id, status='waiting').first()
    if existing:
        return jsonify({'success': True, 'message': 'You are already on the waitlist.'})
    db.session.add(WaitlistEntry(user_id=current_user.id, event_id=event.id))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Added to the event waitlist.'})


@features_bp.get('/features/event/<int:event_id>/waitlist-position')
@user_only
@login_required
def waitlist_position(event_id):
    entry = WaitlistEntry.query.filter_by(user_id=current_user.id, event_id=event_id, status='waiting').first()
    if not entry:
        return jsonify({'success': True, 'position': None})
    ahead = WaitlistEntry.query.filter(WaitlistEntry.event_id == event_id,
                                      WaitlistEntry.status == 'waiting',
                                      WaitlistEntry.joined_at < entry.joined_at).count()
    return jsonify({'success': True, 'position': ahead + 1})


@features_bp.get('/features/event/<int:event_id>/feedback')
@login_required
def feedback_page(event_id):
    event = Event.query.get_or_404(event_id)
    existing = Feedback.query.filter_by(user_id=current_user.id, event_id=event_id).first() if isinstance(current_user, User) else None
    return render_template('user/feedback.html', event=event, existing=existing)
