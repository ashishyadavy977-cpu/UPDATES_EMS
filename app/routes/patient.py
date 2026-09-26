from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app.models import db, Patient, MedicalRecord, Admin
from datetime import datetime, date
from sqlalchemy import or_
import os

patient_bp = Blueprint('patient', __name__, url_prefix='/admin/patients', template_folder='../templates')


def is_admin():
    """Check if current user is admin"""
    return isinstance(current_user, Admin)


@patient_bp.route('/')
@login_required
def list_patients():
    """List all patients with pagination and search"""
    if not is_admin():
        flash('Unauthorized access', 'danger')
        return redirect(url_for('auth.login'))
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    
    query = Patient.query
    
    if search:
        query = query.filter(
            or_(
                Patient.patient_id.ilike(f'%{search}%'),
                Patient.first_name.ilike(f'%{search}%'),
                Patient.last_name.ilike(f'%{search}%'),
                Patient.email.ilike(f'%{search}%'),
                Patient.phone.ilike(f'%{search}%')
            )
        )
    
    if status_filter and status_filter in ['active', 'inactive', 'discharged']:
        query = query.filter_by(status=status_filter)
    
    # Sort by creation date (newest first)
    query = query.order_by(Patient.created_at.desc())
    
    patients = query.paginate(page=page, per_page=10)
    
    return render_template('admin/patients/list.html',
                         patients=patients,
                         search=search,
                         status_filter=status_filter)


@patient_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_patient():
    """Add new patient"""
    if not is_admin():
        flash('Unauthorized access', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        try:
            # Generate patient ID
            last_patient = Patient.query.order_by(Patient.id.desc()).first()
            patient_number = (last_patient.id + 1) if last_patient else 1
            patient_id = f"PAT{patient_number:05d}"
            
            # Check if email is already used (if provided)
            if request.form.get('email'):
                existing = Patient.query.filter_by(email=request.form.get('email')).first()
                if existing:
                    flash('Email already exists', 'danger')
                    return redirect(url_for('patient.add_patient'))
            
            patient = Patient(
                patient_id=patient_id,
                first_name=request.form.get('first_name').strip(),
                last_name=request.form.get('last_name').strip(),
                date_of_birth=datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date(),
                gender=request.form.get('gender'),
                email=request.form.get('email').strip() if request.form.get('email') else None,
                phone=request.form.get('phone').strip(),
                address=request.form.get('address').strip(),
                city=request.form.get('city').strip(),
                state=request.form.get('state').strip(),
                postal_code=request.form.get('postal_code').strip(),
                blood_group=request.form.get('blood_group') if request.form.get('blood_group') else None,
                allergies=request.form.get('allergies').strip() if request.form.get('allergies') else None,
                chronic_conditions=request.form.get('chronic_conditions').strip() if request.form.get('chronic_conditions') else None,
                emergency_contact_name=request.form.get('emergency_contact_name').strip(),
                emergency_contact_phone=request.form.get('emergency_contact_phone').strip(),
                insurance_provider=request.form.get('insurance_provider').strip() if request.form.get('insurance_provider') else None,
                insurance_policy_number=request.form.get('insurance_policy_number').strip() if request.form.get('insurance_policy_number') else None,
                notes=request.form.get('notes').strip() if request.form.get('notes') else None,
                status='active'
            )
            
            db.session.add(patient)
            db.session.commit()
            
            flash(f'Patient {patient.full_name} added successfully with ID: {patient_id}', 'success')
            return redirect(url_for('patient.view_patient', patient_id=patient.id))
            
        except ValueError as e:
            flash(f'Invalid input: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding patient: {str(e)}', 'danger')
    
    return render_template('admin/patients/add.html')


@patient_bp.route('/<int:patient_id>/view')
@login_required
def view_patient(patient_id):
    """View patient details"""
    if not is_admin():
        flash('Unauthorized access', 'danger')
        return redirect(url_for('auth.login'))
    
    patient = Patient.query.get_or_404(patient_id)
    medical_records = MedicalRecord.query.filter_by(patient_id=patient_id).order_by(
        MedicalRecord.visit_date.desc()
    ).all()
    
    return render_template('admin/patients/view.html',
                         patient=patient,
                         medical_records=medical_records)


@patient_bp.route('/<int:patient_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    """Edit patient information"""
    if not is_admin():
        flash('Unauthorized access', 'danger')
        return redirect(url_for('auth.login'))
    
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        try:
            # Check if new email is already used
            new_email = request.form.get('email').strip() if request.form.get('email') else None
            if new_email and new_email != patient.email:
                existing = Patient.query.filter_by(email=new_email).first()
                if existing:
                    flash('Email already exists', 'danger')
                    return redirect(url_for('patient.edit_patient', patient_id=patient_id))
            
            patient.first_name = request.form.get('first_name').strip()
            patient.last_name = request.form.get('last_name').strip()
            patient.date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date()
            patient.gender = request.form.get('gender')
            patient.email = new_email
            patient.phone = request.form.get('phone').strip()
            patient.address = request.form.get('address').strip()
            patient.city = request.form.get('city').strip()
            patient.state = request.form.get('state').strip()
            patient.postal_code = request.form.get('postal_code').strip()
            patient.blood_group = request.form.get('blood_group') if request.form.get('blood_group') else None
            patient.allergies = request.form.get('allergies').strip() if request.form.get('allergies') else None
            patient.chronic_conditions = request.form.get('chronic_conditions').strip() if request.form.get('chronic_conditions') else None
            patient.emergency_contact_name = request.form.get('emergency_contact_name').strip()
            patient.emergency_contact_phone = request.form.get('emergency_contact_phone').strip()
            patient.insurance_provider = request.form.get('insurance_provider').strip() if request.form.get('insurance_provider') else None
            patient.insurance_policy_number = request.form.get('insurance_policy_number').strip() if request.form.get('insurance_policy_number') else None
            patient.notes = request.form.get('notes').strip() if request.form.get('notes') else None
            patient.status = request.form.get('status')
            
            db.session.commit()
            
            flash(f'Patient {patient.full_name} updated successfully', 'success')
            return redirect(url_for('patient.view_patient', patient_id=patient.id))
            
        except ValueError as e:
            flash(f'Invalid input: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating patient: {str(e)}', 'danger')
    
    return render_template('admin/patients/edit.html', patient=patient)


@patient_bp.route('/<int:patient_id>/delete', methods=['POST'])
@login_required
def delete_patient(patient_id):
    """Delete patient (soft delete - change status)"""
    if not is_admin():
        flash('Unauthorized access', 'danger')
        return redirect(url_for('auth.login'))
    
    patient = Patient.query.get_or_404(patient_id)
    
    try:
        # Soft delete - mark as discharged instead of removing
        patient.status = 'discharged'
        db.session.commit()
        
        flash(f'Patient {patient.full_name} has been marked as discharged', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting patient: {str(e)}', 'danger')
    
    return redirect(url_for('patient.list_patients'))


@patient_bp.route('/<int:patient_id>/add-record', methods=['GET', 'POST'])
@login_required
def add_medical_record(patient_id):
    """Add medical record for patient"""
    if not is_admin():
        flash('Unauthorized access', 'danger')
        return redirect(url_for('auth.login'))
    
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        try:
            record = MedicalRecord(
                patient_id=patient_id,
                doctor_name=request.form.get('doctor_name').strip(),
                diagnosis=request.form.get('diagnosis').strip(),
                symptoms=request.form.get('symptoms').strip() if request.form.get('symptoms') else None,
                treatment=request.form.get('treatment').strip(),
                medications=request.form.get('medications').strip() if request.form.get('medications') else None,
                notes=request.form.get('notes').strip() if request.form.get('notes') else None
            )
            
            db.session.add(record)
            db.session.commit()
            
            flash('Medical record added successfully', 'success')
            return redirect(url_for('patient.view_patient', patient_id=patient_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding medical record: {str(e)}', 'danger')
    
    return render_template('admin/patients/add_record.html', patient=patient)


@patient_bp.route('/record/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_medical_record(record_id):
    """Edit medical record"""
    if not is_admin():
        flash('Unauthorized access', 'danger')
        return redirect(url_for('auth.login'))
    
    record = MedicalRecord.query.get_or_404(record_id)
    patient_id = record.patient_id
    
    if request.method == 'POST':
        try:
            record.doctor_name = request.form.get('doctor_name').strip()
            record.diagnosis = request.form.get('diagnosis').strip()
            record.symptoms = request.form.get('symptoms').strip() if request.form.get('symptoms') else None
            record.treatment = request.form.get('treatment').strip()
            record.medications = request.form.get('medications').strip() if request.form.get('medications') else None
            record.notes = request.form.get('notes').strip() if request.form.get('notes') else None
            
            db.session.commit()
            
            flash('Medical record updated successfully', 'success')
            return redirect(url_for('patient.view_patient', patient_id=patient_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating medical record: {str(e)}', 'danger')
    
    return render_template('admin/patients/edit_record.html', record=record)


@patient_bp.route('/record/<int:record_id>/delete', methods=['POST'])
@login_required
def delete_medical_record(record_id):
    """Delete medical record"""
    if not is_admin():
        flash('Unauthorized access', 'danger')
        return redirect(url_for('auth.login'))
    
    record = MedicalRecord.query.get_or_404(record_id)
    patient_id = record.patient_id
    
    try:
        db.session.delete(record)
        db.session.commit()
        
        flash('Medical record deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting medical record: {str(e)}', 'danger')
    
    return redirect(url_for('patient.view_patient', patient_id=patient_id))


@patient_bp.route('/api/search')
@login_required
def search_patients_api():
    """API endpoint for searching patients (for autocomplete, etc.)"""
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    patients = Patient.query.filter(
        or_(
            Patient.patient_id.ilike(f'%{query}%'),
            Patient.first_name.ilike(f'%{query}%'),
            Patient.last_name.ilike(f'%{query}%'),
            Patient.email.ilike(f'%{query}%')
        )
    ).limit(10).all()
    
    return jsonify([{
        'id': p.id,
        'patient_id': p.patient_id,
        'name': p.full_name,
        'age': p.age,
        'phone': p.phone
    } for p in patients])


@patient_bp.route('/stats')
@login_required
def patient_stats():
    """Get patient statistics"""
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    total_patients = Patient.query.count()
    active_patients = Patient.query.filter_by(status='active').count()
    inactive_patients = Patient.query.filter_by(status='inactive').count()
    discharged_patients = Patient.query.filter_by(status='discharged').count()
    
    return jsonify({
        'total_patients': total_patients,
        'active_patients': active_patients,
        'inactive_patients': inactive_patients,
        'discharged_patients': discharged_patients
    })
