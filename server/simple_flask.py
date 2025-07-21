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

def create_audit_folder(application_id, audit_name):
    """Create audit folder for storing files"""
    # Use application ID and sanitized audit name for folder
    sanitized_name = secure_filename(audit_name.replace(' ', '_'))
    folder_name = f"audit_{application_id}_{sanitized_name}"
    folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def save_uploaded_file(file, folder_path, file_type):
    """Save uploaded file to audit folder"""
    if file and allowed_file(file.filename):
        # Create unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{file_type}_{timestamp}_{name}{ext}"
        
        file_path = os.path.join(folder_path, unique_filename)
        file.save(file_path)
        return file_path, unique_filename
    return None, None

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
                   start_date, end_date, enable_followup_questions, created_at 
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
                'enableFollowupQuestions': row['enable_followup_questions'] or False,
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
        # Extract follow-up questions setting
        settings = data.get('settings', {})
        enable_followup = settings.get('enableFollowUpQuestions', False)
        
        cursor.execute("""
            INSERT INTO applications (name, audit_name, ci_id, start_date, end_date, enable_followup_questions)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, name, audit_name, ci_id, start_date, end_date, enable_followup_questions, created_at
        """, (
            data.get('name') or data['auditName'],  # Use name if provided, otherwise auditName
            data['auditName'],
            data['ciId'],
            data.get('startDate') or data.get('auditDateFrom'),
            data.get('endDate') or data.get('auditDateTo'),
            enable_followup
        ))
        
        row = cursor.fetchone()
        conn.commit()
        
        # Create audit folder for file storage
        audit_folder = create_audit_folder(row['id'], row['audit_name'])
        
        app_data = {
            'id': row['id'],
            'auditName': row['audit_name'],
            'ciId': row['ci_id'],
            'auditDateFrom': row['start_date'],
            'auditDateTo': row['end_date'],
            'enableFollowupQuestions': row['enable_followup_questions'],
            'createdAt': row['created_at'],
            'auditFolder': audit_folder
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
                   start_date, end_date, enable_followup_questions, created_at 
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
            'enableFollowupQuestions': row['enable_followup_questions'] or False,
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
        
        # Extract follow-up questions setting
        settings = data.get('settings', {})
        enable_followup = settings.get('enableFollowUpQuestions', False)
        
        # Update the application
        cursor.execute("""
            UPDATE applications 
            SET name = %s, audit_name = %s, ci_id = %s, start_date = %s, end_date = %s, enable_followup_questions = %s
            WHERE id = %s
            RETURNING id, name, audit_name, ci_id, start_date, end_date, enable_followup_questions, created_at
        """, (
            data.get('name') or data['auditName'],
            data['auditName'],
            data['ciId'],
            data.get('startDate') or data.get('auditDateFrom'),
            data.get('endDate') or data.get('auditDateTo'),
            enable_followup,
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
            'enableFollowupQuestions': row['enable_followup_questions'],
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
        
        # Get application info to create audit folder
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT audit_name FROM applications WHERE id = %s", (application_id,))
        app_row = cursor.fetchone()
        
        if not app_row:
            return jsonify({'error': 'Application not found'}), 404
        
        # Create audit folder and save file
        audit_folder = create_audit_folder(application_id, app_row['audit_name'])
        file_path, unique_filename = save_uploaded_file(file, audit_folder, file_type)
        
        if not file_path:
            return jsonify({'error': 'Failed to save file'}), 500
        
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
            
            # Insert data request record
            cursor.execute("""
                INSERT INTO data_requests 
                (application_id, file_name, file_size, file_type, questions, 
                 total_questions, categories, subcategories, column_mappings, file_path, uploaded_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, file_name, total_questions
            """, (
                application_id,
                unique_filename,
                os.path.getsize(file_path),
                file_type,
                json.dumps(questions),
                len(questions),
                json.dumps(list(categories)),
                json.dumps(list(subcategories)),
                json.dumps(column_mappings),
                file_path,
                datetime.now()
            ))
            
            result = cursor.fetchone()
            conn.commit()
            
            return jsonify({
                'id': result['id'],
                'fileName': result['file_name'],
                'totalQuestions': result['total_questions'],
                'message': 'File processed successfully',
                'filePath': file_path
            }), 201
            
        finally:
            # Note: File is kept in audit folder, not removed
            
            if conn:
                cursor.close()
                conn.close()
                
    except Exception as e:
        return jsonify({
            'error': f'Error processing Excel file: {str(e)}'
        }), 500

# Question analysis API endpoints using OpenAI
@app.route('/api/questions/analyze', methods=['POST'])
def analyze_questions_with_ai():
    """Analyze questions using OpenAI to determine tools and prompts"""
    try:
        data = request.get_json()
        application_id = data.get('applicationId')
        questions = data.get('questions', [])
        
        if not application_id or not questions:
            return jsonify({'error': 'Application ID and questions are required'}), 400
        
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        analyses = []
        
        for question in questions:
            try:
                # Create AI prompt for analysis
                system_prompt = """You are an expert audit data collection specialist. For each audit question, you need to:

1. Determine the most appropriate tool for data collection
2. Create a specific prompt for an AI agent to collect the required data
3. Explain why this tool/connector is needed

Available tools:
- sql_server: For querying SQL Server databases
- oracle_db: For querying Oracle databases  
- gnosis: For searching document repositories
- jira: For accessing Jira tickets and project data
- qtest: For test management and quality assurance data
- service_now: For ITSM and service management data

Respond in JSON format with:
{
  "toolSuggestion": "tool_id",
  "aiPrompt": "Specific instructions for AI agent data collection",
  "connectorReason": "Why this tool/connector is appropriate",
  "category": "Main category of the question",
  "subcategory": "Specific subcategory"
}"""

                user_prompt = f"""Analyze this audit question:

Question Number: {question.get('questionNumber', '')}
Process: {question.get('process', '')}
Sub-Process: {question.get('subProcess', '')}
Question: {question.get('question', '')}

Determine the best tool for data collection and create an appropriate AI agent prompt."""

                response = client.chat.completions.create(
                    model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                
                ai_analysis = json.loads(response.choices[0].message.content)
                
                analysis = {
                    'questionId': question.get('id', ''),
                    'originalQuestion': question.get('question', ''),
                    'category': ai_analysis.get('category', question.get('process', '')),
                    'subcategory': ai_analysis.get('subcategory', question.get('subProcess', '')),
                    'aiPrompt': ai_analysis.get('aiPrompt', ''),
                    'toolSuggestion': ai_analysis.get('toolSuggestion', 'sql_server'),
                    'connectorReason': ai_analysis.get('connectorReason', ''),
                    'connectorToUse': ai_analysis.get('toolSuggestion', 'sql_server')
                }
                
                analyses.append(analysis)
                
            except Exception as e:
                print(f"Error analyzing question {question.get('id', '')}: {e}")
                # Fallback analysis
                analyses.append({
                    'questionId': question.get('id', ''),
                    'originalQuestion': question.get('question', ''),
                    'category': question.get('process', ''),
                    'subcategory': question.get('subProcess', ''),
                    'aiPrompt': f"Collect data to answer: {question.get('question', '')}",
                    'toolSuggestion': 'sql_server',
                    'connectorReason': 'Default suggestion - requires manual review',
                    'connectorToUse': 'sql_server'
                })
        
        return jsonify({
            'analyses': analyses,
            'total': len(analyses)
        }), 200
        
    except Exception as e:
        print(f"Error in analyze_questions_with_ai: {e}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/questions/analyses/<int:application_id>', methods=['GET'])
def get_question_analyses(application_id):
    """Get saved question analyses for application"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT question_id, original_question, category, subcategory,
                   ai_prompt, tool_suggestion, connector_reason, connector_to_use
            FROM question_analyses 
            WHERE application_id = %s
            ORDER BY question_id
        """, (application_id,))
        
        analyses = []
        for row in cursor.fetchall():
            analysis_data = {
                'id': row['question_id'],
                'originalQuestion': row['original_question'],
                'category': row['category'],
                'subcategory': row['subcategory'],
                'prompt': row['ai_prompt'],
                'toolSuggestion': row['tool_suggestion'],
                'connectorReason': row['connector_reason'],
                'connectorToUse': row['connector_to_use']
            }
            analyses.append(analysis_data)
        
        return jsonify(analyses), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

@app.route('/api/questions/analyze', methods=['POST'])
def analyze_questions():
    """Analyze questions with AI (mock implementation)"""
    try:
        data = request.get_json()
        application_id = data.get('applicationId')
        
        if not application_id:
            return jsonify({'error': 'Application ID is required'}), 400
        
        # Get questions from data_requests table
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT questions FROM data_requests 
            WHERE application_id = %s AND file_type = 'primary'
            ORDER BY uploaded_at DESC LIMIT 1
        """, (application_id,))
        
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': 'No questions found for this application'}), 404
        
        questions = result['questions']
        if isinstance(questions, str):
            questions = json.loads(questions)
        
        # Mock AI analysis - in real implementation, this would use OpenAI
        analyzed_questions = []
        for q in questions:
            analyzed_q = {
                'id': q.get('id', ''),
                'originalQuestion': q.get('question', ''),
                'category': q.get('process', 'General'),
                'subcategory': q.get('subProcess', ''),
                'prompt': f"Analyze the following audit question and provide detailed guidance: {q.get('question', '')}",
                'toolSuggestion': 'sql_server',  # Default suggestion
                'connectorReason': 'This question requires database analysis to verify compliance.',
                'connectorToUse': 'sql_server'
            }
            analyzed_questions.append(analyzed_q)
        
        return jsonify({
            'questions': analyzed_questions,
            'totalQuestions': len(analyzed_questions)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

@app.route('/api/questions/analyses/save', methods=['POST'])
def save_question_analyses():
    """Save question analyses to database"""
    try:
        data = request.get_json()
        application_id = data.get('applicationId')
        analyses = data.get('analyses', [])
        
        if not application_id:
            return jsonify({'error': 'Application ID is required'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Delete existing analyses for this application
        cursor.execute("DELETE FROM question_analyses WHERE application_id = %s", (application_id,))
        
        # Insert new analyses with unique identifiers
        for idx, analysis in enumerate(analyses):
            # Create unique question_id by combining original id with index
            unique_question_id = f"{analysis.get('questionId', analysis.get('id', f'Q{idx+1}'))}-{idx}"
            
            cursor.execute("""
                INSERT INTO question_analyses 
                (application_id, question_id, original_question, category, subcategory,
                 ai_prompt, tool_suggestion, connector_reason, connector_to_use)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                application_id,
                unique_question_id,
                analysis.get('originalQuestion', ''),
                analysis.get('category', ''),
                analysis.get('subcategory', ''),
                analysis.get('aiPrompt', ''),
                analysis.get('toolSuggestion', ''),
                analysis.get('connectorReason', ''),
                analysis.get('connectorToUse', '')
            ))
        
        conn.commit()
        
        return jsonify({
            'message': 'Analyses saved successfully',
            'count': len(analyses)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

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

# AI Agent Execution API
@app.route('/api/agents/execute', methods=['POST'])
def execute_agent():
    """Execute AI agent for data collection"""
    try:
        data = request.get_json()
        application_id = data.get('applicationId')
        question_id = data.get('questionId')
        prompt = data.get('prompt')
        tool_type = data.get('toolType')
        connector_id = data.get('connectorId')
        
        if not all([application_id, question_id, prompt, tool_type, connector_id]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Get connector details
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT name, type, config FROM tool_connectors 
            WHERE id = %s
        """, (connector_id,))
        
        connector = cursor.fetchone()
        if not connector:
            return jsonify({'error': 'Connector not found'}), 404
        
        # Create AI agent prompt based on tool type
        system_prompt = f"""You are an expert data collection agent specializing in {tool_type}. 
Your task is to collect specific audit data based on the given prompt.

Connector: {connector['name']} ({connector['type']})
Configuration: {connector['config'] if connector['config'] else 'Default configuration'}

Provide a detailed response about what data would be collected, how it would be queried/accessed, 
and what the expected results would look like. Format your response as a structured data collection report."""

        user_prompt = f"""Execute the following data collection task:

{prompt}

Please provide:
1. Data collection method and approach
2. Expected data sources and queries/searches
3. Sample of what the collected data would contain
4. Number of records or data points expected
5. Any potential challenges or limitations"""

        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        ai_response = response.choices[0].message.content
        
        # Store execution result in database
        cursor.execute("""
            INSERT INTO agent_executions 
            (application_id, question_id, tool_type, connector_id, prompt, result, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """, (
            application_id,
            question_id,
            tool_type,
            connector_id,
            prompt,
            ai_response,
            'completed'
        ))
        
        conn.commit()
        
        return jsonify({
            'status': 'completed',
            'result': {
                'data': ai_response,
                'connector': connector['name'],
                'tool_type': tool_type,
                'records': 'Varies based on query',
                'timestamp': datetime.now().isoformat()
            }
        }), 200
        
    except Exception as e:
        print(f"Error in execute_agent: {e}")
        return jsonify({'error': f'Agent execution failed: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

# Get agent execution results
@app.route('/api/agents/executions/<int:application_id>', methods=['GET'])
def get_agent_executions(application_id):
    """Get all agent execution results for an application"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT ae.*, tc.name as connector_name
            FROM agent_executions ae
            LEFT JOIN tool_connectors tc ON ae.connector_id = tc.id
            WHERE ae.application_id = %s
            ORDER BY ae.created_at DESC
        """, (application_id,))
        
        executions = []
        for row in cursor.fetchall():
            execution_data = {
                'id': row['id'],
                'questionId': row['question_id'],
                'toolType': row['tool_type'],
                'connectorName': row['connector_name'],
                'prompt': row['prompt'],
                'result': row['result'],
                'status': row['status'],
                'createdAt': row['created_at']
            }
            executions.append(execution_data)
        
        return jsonify(executions), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == '__main__':
    print("🐍 Starting Simple Flask API server...")
    print("📡 CORS enabled for React frontend at http://localhost:5000")
    print("🔗 Flask backend running at http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)