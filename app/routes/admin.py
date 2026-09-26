from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
from app.models import db, Event, User, Registration, Admin
from app.utils import save_event_image, delete_file
from datetime import datetime
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='../templates/admin')


def admin_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Admin):
            flash('Admin access required', 'danger')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with statistics"""
    total_users = User.query.count()
    total_events = Event.query.count()
    total_registrations = Registration.query.count()
    
    events = Event.query.order_by(Event.created_at.desc()).limit(5).all()
    recent_registrations = Registration.query.order_by(
        Registration.registration_date.desc()
    ).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_events=total_events,
                         total_registrations=total_registrations,
                         events=events,
                         recent_registrations=recent_registrations)


@admin_bp.route('/events')
@admin_required
def events():
    """Manage events"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    
    query = Event.query
    
    if search:
        query = query.filter(Event.event_name.ilike(f'%{search}%'))
    
    events = query.order_by(Event.created_at.desc()).paginate(page=page, per_page=10)
    
    return render_template('admin/events.html', events=events, search=search)


@admin_bp.route('/event/create', methods=['GET', 'POST'])
@admin_required
def create_event():
    """Create new event"""
    if request.method == 'POST':
        event_name = request.form.get('event_name', '').strip()
        event_date = request.form.get('event_date', '').strip()
        event_time = request.form.get('event_time', '').strip()
        venue = request.form.get('venue', '').strip()
        description = request.form.get('description', '').strip()
        capacity = request.form.get('capacity', 100, type=int)
        
        image_filename = None
        if 'image' in request.files:
            image = request.files['image']
            image_filename = save_event_image(image)
        
        errors = []
        if not event_name:
            errors.append('Event name is required')
        if not event_date:
            errors.append('Event date is required')
        if not event_time:
            errors.append('Event time is required')
        if not venue:
            errors.append('Venue is required')
        if capacity < 1:
            errors.append('Capacity must be at least 1')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('admin/create_event.html')
        
        try:
            event = Event(
                event_name=event_name,
                event_date=datetime.strptime(event_date, '%Y-%m-%d').date(),
                event_time=datetime.strptime(event_time, '%H:%M').time(),
                venue=venue,
                description=description,
                image_filename=image_filename,
                capacity=capacity
            )
            db.session.add(event)
            db.session.commit()
            
            flash('Event created successfully!', 'success')
            return redirect(url_for('admin.events'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating event: {str(e)}', 'danger')
    
    return render_template('admin/create_event.html')


@admin_bp.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_event(event_id):
    """Edit event"""
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        event.event_name = request.form.get('event_name', '').strip()
        event.venue = request.form.get('venue', '').strip()
        event.description = request.form.get('description', '').strip()
        event.capacity = request.form.get('capacity', event.capacity, type=int)
        
        try:
            event_date = request.form.get('event_date', '').strip()
            if event_date:
                event.event_date = datetime.strptime(event_date, '%Y-%m-%d').date()
            
            event_time = request.form.get('event_time', '').strip()
            if event_time:
                event.event_time = datetime.strptime(event_time, '%H:%M').time()
        except ValueError:
            flash('Invalid date or time format', 'danger')
            return render_template('admin/edit_event.html', event=event)
        
        if 'image' in request.files and request.files['image'].filename:
            image = request.files['image']
            if image.filename:
                new_filename = save_event_image(image)
                if new_filename:
                    if event.image_filename:
                        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'],
                                               event.image_filename)
                        delete_file(old_path)
                    event.image_filename = new_filename
        
        try:
            db.session.commit()
            flash('Event updated successfully!', 'success')
            return redirect(url_for('admin.events'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating event: {str(e)}', 'danger')
    
    return render_template('admin/edit_event.html', event=event)


@admin_bp.route('/event/<int:event_id>/delete', methods=['POST'])
@admin_required
def delete_event(event_id):
    """Delete event"""
    event = Event.query.get_or_404(event_id)
    
    try:
        if event.image_filename:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'],
                                     event.image_filename)
            delete_file(image_path)
        
        for registration in event.registrations:
            if registration.qr_code_filename:
                qr_path = os.path.join(current_app.config['QRCODE_FOLDER'],
                                      registration.qr_code_filename)
                delete_file(qr_path)
        
        db.session.delete(event)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Event deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/users')
@admin_required
def users():
    """Manage users"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    
    query = User.query
    
    if search:
        query = query.filter(User.email.ilike(f'%{search}%') | 
                            User.name.ilike(f'%{search}%'))
    
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=10)
    
    return render_template('admin/users.html', users=users, search=search)


@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete user and associated data"""
    user = User.query.get_or_404(user_id)
    
    try:
        registrations = Registration.query.filter_by(user_id=user_id).all()
        for registration in registrations:
            if registration.qr_code_filename:
                qr_path = os.path.join(current_app.config['QRCODE_FOLDER'],
                                      registration.qr_code_filename)
                delete_file(qr_path)
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'User deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/registrations')
@admin_required
def registrations():
    """View all registrations"""
    page = request.args.get('page', 1, type=int)
    event_id = request.args.get('event_id', '', type=int)
    
    query = Registration.query
    
    if event_id:
        query = query.filter_by(event_id=event_id)
    
    registrations = query.order_by(
        Registration.registration_date.desc()
    ).paginate(page=page, per_page=20)
    
    events = Event.query.all()
    
    return render_template('admin/registrations.html',
                         registrations=registrations,
                         events=events,
                         selected_event_id=event_id)


@admin_bp.route('/statistics')
@admin_required
def statistics():
    """View detailed statistics"""
    total_users = User.query.count()
    total_events = Event.query.count()
    total_registrations = Registration.query.count()
    
    events_with_registrations = db.session.query(
        Event.event_name,
        db.func.count(Registration.id).label('count')
    ).join(Registration).group_by(Event.id).all()
    
    return render_template('admin/statistics.html',
                         total_users=total_users,
                         total_events=total_events,
                         total_registrations=total_registrations,
                         events_with_registrations=events_with_registrations)
