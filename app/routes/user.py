from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify, current_app
from flask_login import login_required, current_user
from app.models import db, Event, Registration, User
from app.feature_models import WaitlistEntry, Attendance
from app.services import notify_user
from app.utils import generate_qr_code
from datetime import datetime
import os

user_bp = Blueprint('user', __name__, url_prefix='/user', template_folder='../templates/user')


@user_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    if not isinstance(current_user, User):
        return redirect(url_for('auth.login'))
    
    total_registrations = Registration.query.filter_by(user_id=current_user.id).count()
    upcoming_events = db.session.query(Event).join(Registration).filter(
        Registration.user_id == current_user.id,
        Event.event_date >= datetime.now().date()
    ).all()
    
    return render_template('user/dashboard.html',
                         total_registrations=total_registrations,
                         upcoming_events=upcoming_events)


@user_bp.route('/events')
@login_required
def events():
    """Browse all events"""
    if not isinstance(current_user, User):
        return redirect(url_for('auth.login'))
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    
    query = Event.query
    
    if search:
        query = query.filter(Event.event_name.ilike(f'%{search}%') | 
                            Event.venue.ilike(f'%{search}%'))
    
    events = query.paginate(page=page, per_page=6)
    
    registered_events = db.session.query(Event.id).join(Registration).filter(
        Registration.user_id == current_user.id
    ).all()
    registered_event_ids = [e[0] for e in registered_events]
    
    return render_template('user/events.html',
                         events=events,
                         registered_event_ids=registered_event_ids,
                         search=search)


@user_bp.route('/event/<int:event_id>')
@login_required
def event_detail(event_id):
    """Event detail page"""
    if not isinstance(current_user, User):
        return redirect(url_for('auth.login'))
    
    event = Event.query.get_or_404(event_id)
    registered = Registration.query.filter_by(
        user_id=current_user.id,
        event_id=event_id
    ).first() is not None
    
    return render_template('user/event_detail.html',
                         event=event,
                         registered=registered)


@user_bp.route('/register/<int:event_id>', methods=['POST'])
@login_required
def register_event(event_id):
    """Register for an event"""
    if not isinstance(current_user, User):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    event = Event.query.get_or_404(event_id)
    
    existing_registration = Registration.query.filter_by(
        user_id=current_user.id,
        event_id=event_id
    ).first()
    
    if existing_registration:
        return jsonify({'success': False, 'message': 'Already registered for this event'}), 400
    
    if event.is_full:
        existing_wait = WaitlistEntry.query.filter_by(user_id=current_user.id, event_id=event_id, status='waiting').first()
        if existing_wait:
            return jsonify({'success': True, 'message': 'Event is full. You are already on the waitlist.'}), 200
        db.session.add(WaitlistEntry(user_id=current_user.id, event_id=event_id))
        db.session.commit()
        return jsonify({'success': True, 'waitlisted': True, 'message': 'Event is full. You have been added to the waitlist.'}), 200
    
    try:
        registration = Registration(user_id=current_user.id, event_id=event_id)
        db.session.add(registration)
        db.session.flush()
        
        qr_filename = generate_qr_code(registration.id, current_user.email, event.event_name)
        registration.qr_code_filename = qr_filename
        
        db.session.commit()
        notify_user(current_user, f'Registration confirmed: {event.event_name}',
                    f'Your registration for {event.event_name} on {event.event_date} at {event.event_time} is confirmed.', event.id)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Registration successful!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@user_bp.route('/my-tickets')
@login_required
def my_tickets():
    """View user's tickets"""
    if not isinstance(current_user, User):
        return redirect(url_for('auth.login'))
    
    registrations = Registration.query.filter_by(user_id=current_user.id).join(Event).all()
    
    return render_template('user/my_tickets.html', registrations=registrations)


@user_bp.route('/download-ticket/<int:registration_id>')
@login_required
def download_ticket(registration_id):
    """Download ticket QR code"""
    if not isinstance(current_user, User):
        return redirect(url_for('auth.login'))
    
    registration = Registration.query.get_or_404(registration_id)
    
    if registration.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('user.my_tickets'))
    
    if not registration.qr_code_filename:
        flash('Ticket not found', 'warning')
        return redirect(url_for('user.my_tickets'))
    
    file_path = os.path.join(current_app.config['QRCODE_FOLDER'], 
                            registration.qr_code_filename)
    
    if not os.path.exists(file_path):
        flash('Ticket file not found', 'warning')
        return redirect(url_for('user.my_tickets'))
    
    return send_file(file_path,
                    as_attachment=True,
                    download_name=f"ticket_{registration_id}.png")


@user_bp.route('/unregister/<int:registration_id>', methods=['POST'])
@login_required
def unregister(registration_id):
    """Cancel registration"""
    if not isinstance(current_user, User):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    registration = Registration.query.get_or_404(registration_id)
    
    if registration.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        if registration.qr_code_filename:
            qr_path = os.path.join(current_app.config['QRCODE_FOLDER'],
                                  registration.qr_code_filename)
            if os.path.exists(qr_path):
                os.remove(qr_path)
        
        event = registration.event
        db.session.delete(registration)
        db.session.flush()
        # Promote the oldest waiting user into the freed seat.
        candidate = (WaitlistEntry.query.filter_by(event_id=event.id, status='waiting')
                     .order_by(WaitlistEntry.joined_at.asc()).first())
        promoted = None
        if candidate:
            promoted = Registration(user_id=candidate.user_id, event_id=event.id)
            db.session.add(promoted)
            db.session.flush()
            promoted.qr_code_filename = generate_qr_code(promoted.id, candidate.user.email, event.event_name)
            candidate.status = 'promoted'
            candidate.promoted_at = datetime.utcnow()
            notify_user(candidate.user, f'You are confirmed for {event.event_name}',
                        f'A seat opened for {event.event_name} on {event.event_date} at {event.event_time}. Your registration is now confirmed.', event.id)
        db.session.commit()
        message = 'Registration cancelled' + ('; next waitlisted user was promoted.' if promoted else '')
        return jsonify({'success': True, 'message': message}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@user_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    if not isinstance(current_user, User):
        return redirect(url_for('auth.login'))
    
    return render_template('user/profile.html', user=current_user)


@user_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    if not isinstance(current_user, User):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        current_user.name = request.form.get('name', '').strip()
        current_user.phone = request.form.get('phone', '').strip()
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Profile updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@user_bp.before_request
def check_user_type():
    """Ensure only User type can access these routes"""
    if current_user.is_authenticated and not isinstance(current_user, User):
        return redirect(url_for('admin.dashboard'))
