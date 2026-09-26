import os
import qrcode
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_event_image(file):
    """Save event image and return filename"""
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        return None
    
    filename = secure_filename(file.filename)
    filename = f"{os.urandom(8).hex()}_{filename}"
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    try:
        # Optimize image
        img = Image.open(file)
        img.thumbnail((800, 600))
        img.save(filepath, quality=85)
        return filename
    except Exception as e:
        print(f"Error saving image: {e}")
        return None


def generate_qr_code(registration_id, user_email, event_name):
    """Generate QR code for ticket"""
    try:
        qr_data = f"REG_{registration_id}_{user_email}_{event_name}"
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        filename = f"qr_{registration_id}.png"
        filepath = os.path.join(current_app.config['QRCODE_FOLDER'], filename)
        
        img.save(filepath)
        return filename
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None


def delete_file(filepath):
    """Delete file from filesystem"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception as e:
        print(f"Error deleting file: {e}")
    return False
