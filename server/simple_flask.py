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
            INSERT INTO applications (name, audit_name, ci_id, start_date, end_date)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, name, audit_name, ci_id, start_date, end_date, created_at
        """, (
            data.get('name') or data['auditName'],  # Use name if provided, otherwise auditName
            data['auditName'],
            data['ciId'],
            data.get('startDate') or data.get('auditDateFrom'),
            data.get('endDate') or data.get('auditDateTo')
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
            SELECT id, name, audit_name, ci_id, 
                   start_date, end_date, created_at 
            FROM applications 
            WHERE id = %s
        """, (application_id,))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({'error': 'Application not found'}), 404
        
        app_data = {
            'id': row['id'],
            'name': row['name'],
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

@app.route('/api/applications/<int:application_id>', methods=['PUT'])
def update_application(application_id):
    """Update existing application"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # First check if application exists
        cursor.execute("SELECT id FROM applications WHERE id = %s", (application_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Application not found'}), 404
        
        # Update the application
        cursor.execute("""
            UPDATE applications 
            SET name = %s, audit_name = %s, ci_id = %s, start_date = %s, end_date = %s
            WHERE id = %s
            RETURNING id, name, audit_name, ci_id, start_date, end_date, created_at
        """, (
            data.get('name') or data['auditName'],
            data['auditName'],
            data['ciId'],
            data.get('startDate') or data.get('auditDateFrom'),
            data.get('endDate') or data.get('auditDateTo'),
            application_id
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
        
        return jsonify(app_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

# Data requests API
@app.route('/api/data-requests/application/<int:application_id>', methods=['GET'])
def get_data_requests(application_id):
    """Get data requests for application"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id, application_id, file_name, file_size, file_type, 
                   questions, total_questions, categories, subcategories, 
                   column_mappings, uploaded_at
            FROM data_requests 
            WHERE application_id = %s
            ORDER BY uploaded_at DESC
        """, (application_id,))
        
        requests = []
        for row in cursor.fetchall():
            request_data = {
                'id': row['id'],
                'applicationId': row['application_id'],
                'fileName': row['file_name'],
                'fileSize': row['file_size'],
                'fileType': row['file_type'],
                'questions': row['questions'],
                'totalQuestions': row['total_questions'],
                'categories': row['categories'],
                'subcategories': row['subcategories'],
                'columnMappings': row['column_mappings'],
                'uploadedAt': row['uploaded_at']
            }
            requests.append(request_data)
        
        return jsonify(requests), 200
        
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
            
            # Convert to records for sample data, handling NaN values
            sample_df = df.head(3).fillna('')  # Replace NaN with empty string
            sample_data = sample_df.to_dict('records')
            
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

@app.route('/api/excel/process', methods=['POST'])
def process_excel():
    """Process Excel file and save to data_requests table"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if not file or not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format. Only .xlsx and .xls files are allowed'}), 400
        
        application_id = request.form.get('applicationId')
        file_type = request.form.get('fileType', 'primary')
        column_mappings_str = request.form.get('columnMappings', '{}')
        
        if not application_id:
            return jsonify({'error': 'Application ID is required'}), 400
        
        try:
            column_mappings = json.loads(column_mappings_str)
        except:
            return jsonify({'error': 'Invalid column mappings format'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"process_{filename}")
        file.save(file_path)
        
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Extract questions based on column mappings
            questions = []
            categories = set()
            subcategories = set()
            
            for index, row in df.iterrows():
                # Helper function to safely convert values to string, handling NaN
                def safe_str(value, default=''):
                    if pd.isna(value) or value is None:
                        return default
                    return str(value)
                
                question_data = {
                    'id': f"Q{index + 1}",
                    'questionNumber': safe_str(row.get(column_mappings.get('questionNumber', ''), f"Q{index + 1}")),
                    'process': safe_str(row.get(column_mappings.get('process', ''), '')),
                    'subProcess': safe_str(row.get(column_mappings.get('subProcess', ''), '')),
                    'question': safe_str(row.get(column_mappings.get('question', ''), ''))
                }
                questions.append(question_data)
                
                # Collect categories and subcategories
                if question_data['process'] and question_data['process'] != '':
                    categories.add(question_data['process'])
                if question_data['subProcess'] and question_data['subProcess'] != '':
                    subcategories.add(question_data['subProcess'])
            
            # Save to database
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Insert data request record
            cursor.execute("""
                INSERT INTO data_requests 
                (application_id, file_name, file_size, file_type, questions, 
                 total_questions, categories, subcategories, column_mappings)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, file_name, total_questions
            """, (
                application_id,
                filename,
                len(file.read()),
                file_type,
                json.dumps(questions),
                len(questions),
                json.dumps(list(categories)),
                json.dumps(list(subcategories)),
                json.dumps(column_mappings)
            ))
            
            result = cursor.fetchone()
            conn.commit()
            
            return jsonify({
                'id': result['id'],
                'fileName': result['file_name'],
                'totalQuestions': result['total_questions'],
                'message': 'File processed successfully'
            }), 201
            
        finally:
            # Clean up temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            if conn:
                cursor.close()
                conn.close()
                
    except Exception as e:
        return jsonify({
            'error': f'Error processing Excel file: {str(e)}'
        }), 500

# Health check
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Simple Flask API'}), 200

# Database health check
@app.route('/api/database/health', methods=['GET'])
def database_health():
    """Database connectivity health check"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'status': 'error',
                'message': 'Unable to connect to database',
                'database_url_present': bool(os.getenv('DATABASE_URL')),
                'error_details': 'Connection failed'
            }), 500
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute('SELECT 1 as test')
        result = cursor.fetchone()
        
        # Get database info
        cursor.execute('SELECT version() as db_version')
        db_version = cursor.fetchone()[0]
        
        # Check if our tables exist
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name IN ('applications', 'data_requests', 'tool_connectors')
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'message': 'Database connection successful',
            'database_url_present': bool(os.getenv('DATABASE_URL')),
            'connection_test': 'passed',
            'database_version': db_version,
            'existing_tables': existing_tables,
            'tables_count': len(existing_tables),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Database connection failed',
            'database_url_present': bool(os.getenv('DATABASE_URL')),
            'error_details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

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