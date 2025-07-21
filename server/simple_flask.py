#!/usr/bin/env python3
"""
Simple Flask API server for audit data collection application
Clean Flask backend with CORS enabled for React frontend
"""

import os
import json
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, origins=[
    "http://localhost:5000", 
    "http://0.0.0.0:5000",
    "https://7148f2c9-02b0-4430-8db4-b17d1ed51f18-00-1f4bz4pbor6xh.riker.replit.dev",
    "http://7148f2c9-02b0-4430-8db4-b17d1ed51f18-00-1f4bz4pbor6xh.riker.replit.dev"
], supports_credentials=True)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    """Get database connection"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            conn = psycopg2.connect(database_url)
        else:
            conn = psycopg2.connect(
                host=os.getenv('PGHOST', 'localhost'),
                database=os.getenv('PGDATABASE', 'postgres'),
                user=os.getenv('PGUSER', 'postgres'),
                password=os.getenv('PGPASSWORD', ''),
                port=os.getenv('PGPORT', '5432')
            )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# Applications API
@app.route('/api/applications', methods=['GET'])
def get_applications():
    """Get all applications"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id, COALESCE(audit_name, name) as audit_name, ci_id, 
                   start_date, end_date, created_at 
            FROM applications 
            ORDER BY created_at DESC
        """)
        
        applications = []
        for row in cursor.fetchall():
            app_data = {
                'id': row['id'],
                'auditName': row['audit_name'],
                'ciId': row['ci_id'],
                'auditDateFrom': row['start_date'],
                'auditDateTo': row['end_date'],
                'enableFollowupQuestions': False,  # Default value
                'createdAt': row['created_at']
            }
            applications.append(app_data)
        
        return jsonify(applications), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

@app.route('/api/applications', methods=['POST'])
def create_application():
    """Create new application"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            INSERT INTO applications (audit_name, ci_id, start_date, end_date)
            VALUES (%s, %s, %s, %s)
            RETURNING id, audit_name, ci_id, start_date, end_date, created_at
        """, (
            data['auditName'],
            data['ciId'],
            data['auditDateFrom'],
            data['auditDateTo']
        ))
        
        row = cursor.fetchone()
        conn.commit()
        
        app_data = {
            'id': row['id'],
            'auditName': row['audit_name'],
            'ciId': row['ci_id'],
            'auditDateFrom': row['start_date'],
            'auditDateTo': row['end_date'],
            'enableFollowupQuestions': False,  # Default value
            'createdAt': row['created_at']
        }
        
        return jsonify(app_data), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

@app.route('/api/applications/<int:application_id>', methods=['GET'])
def get_application(application_id):
    """Get specific application"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id, COALESCE(audit_name, name) as audit_name, ci_id, 
                   start_date, end_date, created_at 
            FROM applications 
            WHERE id = %s
        """, (application_id,))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({'error': 'Application not found'}), 404
        
        app_data = {
            'id': row['id'],
            'auditName': row['audit_name'],
            'ciId': row['ci_id'],
            'auditDateFrom': row['start_date'],
            'auditDateTo': row['end_date'],
            'enableFollowupQuestions': False,  # Default value
            'createdAt': row['created_at']
        }
        
        return jsonify(app_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

# Excel processing API
@app.route('/api/excel/get-columns', methods=['POST'])
def get_excel_columns():
    """Get column names from uploaded Excel file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if not file or not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format. Only .xlsx and .xls files are allowed'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{filename}")
        file.save(file_path)
        
        try:
            # Read Excel file to get columns and sample data
            df = pd.read_excel(file_path, nrows=5)  # Read first 5 rows
            columns = df.columns.tolist()
            
            # Convert to records for sample data
            sample_data = df.head(3).to_dict('records')
            
            return jsonify({
                'columns': columns,
                'sampleData': sample_data,
                'totalRows': len(df)
            }), 200
            
        finally:
            # Clean up temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
                
    except Exception as e:
        return jsonify({
            'error': f'Error reading Excel file: {str(e)}'
        }), 500

# Health check
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Simple Flask API'}), 200

# Test data endpoint
@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify API is working"""
    return jsonify({
        'message': 'Flask API is working correctly',
        'timestamp': datetime.now().isoformat(),
        'database_available': get_db_connection() is not None
    }), 200

if __name__ == '__main__':
    print("🐍 Starting Simple Flask API server...")
    print("📡 CORS enabled for React frontend at http://localhost:5000")
    print("🔗 Flask backend running at http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)