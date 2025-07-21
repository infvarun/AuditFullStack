#!/usr/bin/env python3
"""
Flask API server for audit data collection application
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
CORS(app, origins=["http://localhost:5000", "http://0.0.0.0:5000"])

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
            SELECT id, audit_name, ci_id, audit_date_from, audit_date_to, 
                   enable_followup_questions, created_at 
            FROM applications 
            ORDER BY created_at DESC
        """)
        
        applications = []
        for row in cursor.fetchall():
            app_data = dict(row)
            app_data['auditName'] = app_data.pop('audit_name')
            app_data['ciId'] = app_data.pop('ci_id')
            app_data['auditDateFrom'] = app_data.pop('audit_date_from')
            app_data['auditDateTo'] = app_data.pop('audit_date_to')
            app_data['enableFollowupQuestions'] = app_data.pop('enable_followup_questions')
            app_data['createdAt'] = app_data.pop('created_at')
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
            INSERT INTO applications (audit_name, ci_id, audit_date_from, audit_date_to, enable_followup_questions)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, audit_name, ci_id, audit_date_from, audit_date_to, enable_followup_questions, created_at
        """, (
            data['auditName'],
            data['ciId'],
            data['auditDateFrom'],
            data['auditDateTo'],
            data.get('enableFollowupQuestions', False)
        ))
        
        row = cursor.fetchone()
        conn.commit()
        
        app_data = dict(row)
        app_data['auditName'] = app_data.pop('audit_name')
        app_data['ciId'] = app_data.pop('ci_id')
        app_data['auditDateFrom'] = app_data.pop('audit_date_from')
        app_data['auditDateTo'] = app_data.pop('audit_date_to')
        app_data['enableFollowupQuestions'] = app_data.pop('enable_followup_questions')
        app_data['createdAt'] = app_data.pop('created_at')
        
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
            SELECT id, audit_name, ci_id, audit_date_from, audit_date_to, 
                   enable_followup_questions, created_at 
            FROM applications 
            WHERE id = %s
        """, (application_id,))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({'error': 'Application not found'}), 404
        
        app_data = dict(row)
        app_data['auditName'] = app_data.pop('audit_name')
        app_data['ciId'] = app_data.pop('ci_id')
        app_data['auditDateFrom'] = app_data.pop('audit_date_from')
        app_data['auditDateTo'] = app_data.pop('audit_date_to')
        app_data['enableFollowupQuestions'] = app_data.pop('enable_followup_questions')
        app_data['createdAt'] = app_data.pop('created_at')
        
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
        if not file or file.filename == '':
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

@app.route('/api/excel/process', methods=['POST'])
def process_excel():
    """Process uploaded Excel file with column mappings"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format. Only .xlsx and .xls files are allowed'}), 400
        
        # Get form data
        application_id = request.form.get('applicationId')
        file_type = request.form.get('fileType', 'primary')
        column_mappings = json.loads(request.form.get('columnMappings', '{}'))
        
        if not application_id:
            return jsonify({'error': 'Application ID is required'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Read and process Excel file
            df = pd.read_excel(file_path)
            
            # Extract column mappings
            question_col = column_mappings.get('questionNumber', 'Question Number')
            category_col = column_mappings.get('process', 'Process')
            subcategory_col = column_mappings.get('subProcess', 'Sub-Process')
            question_text_col = column_mappings.get('question', 'Question')
            
            # Validate required columns exist
            missing_cols = []
            for col_name, col_key in [
                (question_col, 'questionNumber'),
                (category_col, 'process'),
                (subcategory_col, 'subProcess'),
                (question_text_col, 'question')
            ]:
                if col_name not in df.columns:
                    missing_cols.append(f"{col_key} -> {col_name}")
            
            if missing_cols:
                return jsonify({
                    'error': f"Missing columns: {', '.join(missing_cols)}",
                    'availableColumns': df.columns.tolist()
                }), 400
            
            # Process questions
            questions = []
            categories = set()
            subcategories = set()
            
            for index, row in df.iterrows():
                # Skip rows with missing essential data
                if pd.isna(row[question_col]) or pd.isna(row[question_text_col]):
                    continue
                    
                question_number = str(row[question_col]).strip()
                category = str(row[category_col]).strip() if not pd.isna(row[category_col]) else "Uncategorized"
                subcategory = str(row[subcategory_col]).strip() if not pd.isna(row[subcategory_col]) else "General"
                question_text = str(row[question_text_col]).strip()
                
                categories.add(category)
                subcategories.add(subcategory)
                
                questions.append({
                    'id': question_number,
                    'question': question_text,
                    'category': category,
                    'subcategory': subcategory
                })
            
            # Save to database
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Insert or update data request
            cursor.execute("""
                INSERT INTO data_requests (
                    application_id, file_name, file_size, file_type, 
                    questions, total_questions, categories, subcategories,
                    column_mappings, uploaded_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (application_id, file_type) 
                DO UPDATE SET 
                    file_name = EXCLUDED.file_name,
                    file_size = EXCLUDED.file_size,
                    questions = EXCLUDED.questions,
                    total_questions = EXCLUDED.total_questions,
                    categories = EXCLUDED.categories,
                    subcategories = EXCLUDED.subcategories,
                    column_mappings = EXCLUDED.column_mappings,
                    uploaded_at = EXCLUDED.uploaded_at
                RETURNING id
            """, (
                int(application_id),
                filename,
                len(file.read()),
                file_type,
                json.dumps(questions),
                len(questions),
                json.dumps(list(categories)),
                json.dumps(list(subcategories)),
                json.dumps(column_mappings),
                datetime.now()
            ))
            
            data_request_id = cursor.fetchone()['id']
            conn.commit()
            
            return jsonify({
                'id': data_request_id,
                'applicationId': int(application_id),
                'fileName': filename,
                'fileType': file_type,
                'questions': questions,
                'totalQuestions': len(questions),
                'categories': list(categories),
                'subcategories': list(subcategories),
                'columnMappings': column_mappings
            }), 200
            
        finally:
            # Clean up file if processing failed
            if os.path.exists(file_path):
                os.remove(file_path)
            
    except Exception as e:
        return jsonify({
            'error': f'Server error: {str(e)}'
        }), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

# Health check
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Flask API'}), 200

if __name__ == '__main__':
    print("🐍 Starting Flask API server...")
    print("📡 CORS enabled for React frontend at http://localhost:5000")
    print("🔗 Flask backend running at http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)