"""
Event Management System - Flask Application Entry Point
Author: Developer
Created: 2026
"""

import os
from dotenv import load_dotenv
from app import create_app
from config import DevelopmentConfig, ProductionConfig

load_dotenv()

env = os.environ.get('FLASK_ENV', 'development')
if env == 'production':
    app = create_app(ProductionConfig)
else:
    app = create_app(DevelopmentConfig)

if __name__ == '__main__':
    # For development only
    app.run(debug=True, host='0.0.0.0', port=5000)
