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
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# Load environment variables
load_dotenv()

# Initialize Langchain OpenAI
llm = ChatOpenAI(
    model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
    api_key=os.getenv('OPENAI_API_KEY'),
    temperature=0.1,
    max_tokens=2000
)

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

@app.route('/api/applications/<int:application_id>', methods=['DELETE'])
def delete_application(application_id):
    """Delete application and all associated data including files"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # First, get application details for folder cleanup
        cursor.execute("""
            SELECT name, audit_name, ci_id
            FROM applications 
            WHERE id = %s
        """, (application_id,))
        
        application = cursor.fetchone()
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        # Start transaction for complete cleanup
        cursor.execute("BEGIN;")
        
        try:
            # Delete agent executions
            cursor.execute("DELETE FROM agent_executions WHERE application_id = %s", (application_id,))
            
            # Delete question analyses
            cursor.execute("DELETE FROM question_analyses WHERE application_id = %s", (application_id,))
            
            # Delete data collection sessions
            cursor.execute("DELETE FROM data_collection_sessions WHERE application_id = %s", (application_id,))
            
            # Delete data requests
            cursor.execute("DELETE FROM data_requests WHERE application_id = %s", (application_id,))
            
            # Delete the application
            cursor.execute("DELETE FROM applications WHERE id = %s", (application_id,))
            
            # Commit database changes
            cursor.execute("COMMIT;")
            
            # Clean up file system - remove audit folder
            import shutil
            audit_folder_name = f"{application['name']}_{application['ci_id']}_{application_id}"
            folder_path = os.path.join('uploads', audit_folder_name)
            
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                print(f"Deleted audit folder: {folder_path}")
            
            return jsonify({
                'success': True,
                'message': f'Application "{application["audit_name"]}" and all associated data deleted successfully',
                'deletedApplicationId': application_id,
                'deletedFolder': audit_folder_name
            })
            
        except Exception as e:
            # Rollback transaction on error
            cursor.execute("ROLLBACK;")
            print(f"Error during deletion transaction: {e}")
            raise e
        
    except Exception as e:
        print(f"Error deleting application {application_id}: {e}")
        return jsonify({'error': f'Failed to delete application: {str(e)}'}), 500
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
        
        # Use Langchain with OpenAI for intelligent question analysis
        analyses = []
        
        # Create Langchain prompt template with better tool selection logic
        system_template = """You are an expert audit data collection specialist. Analyze each audit question and intelligently determine the most appropriate tool based on the question content and context.

TOOL SELECTION GUIDELINES:
- sql_server: Database queries, user data, system logs, transactions, authentication records, access controls
- oracle_db: Enterprise database systems, financial data, ERP systems, large-scale data analysis
- gnosis: Document searches, policies, procedures, manuals, compliance documents, knowledge base
- jira: Project tracking, issue management, bug reports, development workflow, change requests  
- qtest: Quality assurance, test cases, test results, defect tracking, testing documentation
- service_now: IT service management, incidents, service requests, change management, ITSM processes

ANALYSIS APPROACH:
1. Read the question carefully and identify key terms
2. Match question intent with appropriate data source
3. Create specific, actionable prompts for data collection agents
4. Provide clear reasoning for tool selection

Examples:
- "Review user access controls" → sql_server (database security data)
- "Find compliance policies" → gnosis (document repository)
- "Check test coverage" → qtest (testing data)
- "Review incident handling" → service_now (ITSM data)

Respond in JSON format only:
{{
  "toolSuggestion": "exact_tool_id_from_list_above",
  "aiPrompt": "Create comprehensive, actionable instructions for an AI data collection agent. Include specific search criteria, expected data types, analysis requirements, and deliverable format. Make it detailed enough for autonomous execution.",
  "connectorReason": "Clear explanation why this tool is the best choice for this specific question",
  "category": "Primary audit category (e.g., Security, Compliance, Process, Quality)",
  "subcategory": "Specific audit area within the category"
}}"""

        human_template = """Analyze this audit question and select the most appropriate tool:

Question Number: {question_number}
Process: {process}
Sub-Process: {sub_process}
Question: {question}

Consider the question content carefully and match it to the most suitable data source from: sql_server, oracle_db, gnosis, jira, qtest, or service_now."""

        prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
        
        for question in questions:
            try:
                # Generate prompt for this specific question
                formatted_prompt = prompt_template.format_messages(
                    question_number=question.get('questionNumber', ''),
                    process=question.get('process', ''),
                    sub_process=question.get('subProcess', ''),
                    question=question.get('question', '')
                )
                
                # Get AI analysis using Langchain with JSON parsing
                response = llm.invoke(formatted_prompt)
                
                # Parse the JSON response with better error handling
                try:
                    ai_analysis = json.loads(response.content)
                    
                    # Validate that we have a proper tool suggestion
                    valid_tools = ['sql_server', 'oracle_db', 'gnosis', 'jira', 'qtest', 'service_now']
                    if ai_analysis.get('toolSuggestion') not in valid_tools:
                        # If invalid tool, try to map based on question content
                        question_text = question.get('question', '').lower()
                        if any(term in question_text for term in ['database', 'user', 'access', 'login', 'authentication']):
                            ai_analysis['toolSuggestion'] = 'sql_server'
                        elif any(term in question_text for term in ['document', 'policy', 'procedure', 'manual', 'compliance']):
                            ai_analysis['toolSuggestion'] = 'gnosis'
                        elif any(term in question_text for term in ['test', 'quality', 'defect', 'bug', 'qa']):
                            ai_analysis['toolSuggestion'] = 'qtest'
                        elif any(term in question_text for term in ['incident', 'service', 'request', 'itsm', 'change']):
                            ai_analysis['toolSuggestion'] = 'service_now'
                        elif any(term in question_text for term in ['project', 'issue', 'development', 'workflow']):
                            ai_analysis['toolSuggestion'] = 'jira'
                        else:
                            ai_analysis['toolSuggestion'] = 'sql_server'  # Default fallback
                            
                except json.JSONDecodeError as je:
                    print(f"JSON parsing error for question {question.get('id', '')}: {je}")
                    print(f"Raw response: {response.content}")
                    
                    # Intelligent fallback based on question content
                    question_text = question.get('question', '').lower()
                    if any(term in question_text for term in ['database', 'user', 'access', 'login', 'authentication', 'data', 'record']):
                        tool_suggestion = 'sql_server'
                    elif any(term in question_text for term in ['document', 'policy', 'procedure', 'manual', 'compliance', 'guideline']):
                        tool_suggestion = 'gnosis'
                    elif any(term in question_text for term in ['test', 'quality', 'defect', 'bug', 'qa', 'testing']):
                        tool_suggestion = 'qtest'
                    elif any(term in question_text for term in ['incident', 'service', 'request', 'itsm', 'change', 'ticket']):
                        tool_suggestion = 'service_now'
                    elif any(term in question_text for term in ['project', 'issue', 'development', 'workflow', 'jira']):
                        tool_suggestion = 'jira'
                    elif any(term in question_text for term in ['oracle', 'erp', 'financial', 'enterprise']):
                        tool_suggestion = 'oracle_db'
                    else:
                        tool_suggestion = 'sql_server'
                        
                    ai_analysis = {
                        'category': question.get('process', 'General'),
                        'subcategory': question.get('subProcess', 'Unknown'),
                        'toolSuggestion': tool_suggestion,
                        'aiPrompt': f"Execute comprehensive data collection for audit question: {question.get('question', '')}. Search {tool_suggestion} system for relevant records, analyze data patterns, and compile detailed findings with specific evidence and metrics.",
                        'connectorReason': f'Selected {tool_suggestion} based on question content analysis'
                    }
                
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
                    'aiPrompt': f"Execute comprehensive audit data collection: {question.get('question', '')}. Access document repository, search for relevant policies and procedures, extract key findings, and provide detailed compliance assessment.",
                    'toolSuggestion': 'gnosis',  # Default to document repository for unknown questions
                    'connectorReason': 'Fallback selection - review question for optimal tool choice',
                    'connectorToUse': 'gnosis'
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
                'questionId': q.get('id', q.get('questionNumber', f'Q{len(analyzed_questions)+1}')),
                'originalQuestion': q.get('question', ''),
                'category': q.get('process', 'General'),
                'subcategory': q.get('subProcess', ''),
                'aiPrompt': f"Analyze the following audit question and provide detailed guidance: {q.get('question', '')}",
                'toolSuggestion': 'SQL Server DB',  # Updated to new format
                'connectorReason': 'This question requires database analysis to verify compliance.',
                'connectorToUse': 'SQL Server DB'  # Updated to new format
            }
            analyzed_questions.append(analyzed_q)
        
        return jsonify({
            'analyses': analyzed_questions,
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
        
        # Create Langchain prompt template for agent execution
        system_template = """You are an expert data collection agent specializing in {tool_type}. 
Your task is to collect specific audit data based on the given prompt.

Connector: {connector_name} ({connector_type})
Configuration: {connector_config}

Provide a detailed response about what data would be collected, how it would be queried/accessed, 
and what the expected results would look like. Format your response as a structured data collection report."""

        human_template = """Execute the following data collection task:

{prompt}

Please provide:
1. Data collection method and approach
2. Expected data sources and queries/searches
3. Sample of what the collected data would contain
4. Number of records or data points expected
5. Any potential challenges or limitations"""

        # Create and format the prompt
        agent_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
        
        formatted_messages = agent_prompt.format_messages(
            tool_type=tool_type,
            connector_name=connector['name'],
            connector_type=connector['type'],
            connector_config=connector['config'] if connector['config'] else 'Default configuration',
            prompt=prompt
        )
        
        # Execute using Langchain
        response = llm.invoke(formatted_messages)
        ai_response = response.content
        
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

# Tool Connectors API for Settings page
@app.route('/api/connectors', methods=['POST'])
def create_tool_connector():
    """Create new tool connector"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Find application by CI ID
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id FROM applications WHERE ci_id = %s LIMIT 1", (data.get('ciId'),))
        app_row = cursor.fetchone()
        
        if not app_row:
            return jsonify({'error': f'No application found for CI ID: {data.get("ciId")}'}), 404
        
        application_id = app_row['id']
        
        # Get connector name from data, or generate default
        connector_name = data.get('connectorName')
        if not connector_name:
            connector_name = f"{data.get('connectorType', 'Unknown')} - {application_id}"
        
        # Insert tool connector
        cursor.execute("""
            INSERT INTO tool_connectors (application_id, ci_id, connector_name, connector_type, configuration, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, application_id, ci_id, connector_name, connector_type, configuration, status, created_at
        """, (
            application_id,
            data.get('ciId'),
            connector_name,
            data.get('connectorType'),
            json.dumps(data.get('configuration', {})),
            data.get('status', 'pending')
        ))
        
        row = cursor.fetchone()
        conn.commit()
        
        connector_data = {
            'id': row['id'],
            'applicationId': row['application_id'],
            'ciId': row['ci_id'],
            'connectorName': row['connector_name'],
            'connectorType': row['connector_type'],
            'configuration': row['configuration'],
            'status': row['status'],
            'createdAt': row['created_at']
        }
        
        return jsonify(connector_data), 201
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

@app.route('/api/connectors/<int:connector_id>', methods=['PUT'])
def update_tool_connector(connector_id):
    """Update existing tool connector"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Update tool connector
        cursor.execute("""
            UPDATE tool_connectors 
            SET connector_type = %s, configuration = %s, status = %s
            WHERE id = %s
            RETURNING id, application_id, ci_id, connector_type, configuration, status, created_at
        """, (
            data.get('connectorType'),
            json.dumps(data.get('configuration', {})),
            data.get('status', 'pending'),
            connector_id
        ))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({'error': 'Connector not found'}), 404
            
        conn.commit()
        
        connector_data = {
            'id': row['id'],
            'applicationId': row['application_id'],
            'ciId': row['ci_id'],
            'connectorType': row['connector_type'],
            'configuration': row['configuration'],
            'status': row['status'],
            'createdAt': row['created_at']
        }
        
        return jsonify(connector_data), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

@app.route('/api/connectors/<int:connector_id>', methods=['DELETE'])
def delete_tool_connector(connector_id):
    """Delete tool connector"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        
        # Delete tool connector
        cursor.execute("DELETE FROM tool_connectors WHERE id = %s", (connector_id,))
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Connector not found'}), 404
            
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Connector deleted successfully'}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

@app.route('/api/connectors/ci/<ci_id>', methods=['GET'])
def get_connectors_by_ci(ci_id):
    """Get tool connectors for specific CI ID"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id, application_id, ci_id, connector_name, connector_type, configuration, status, created_at
            FROM tool_connectors 
            WHERE ci_id = %s
            ORDER BY created_at DESC
        """, (ci_id,))
        
        connectors = []
        for row in cursor.fetchall():
            connector_data = {
                'id': row['id'],
                'applicationId': row['application_id'],
                'ciId': row['ci_id'],
                'connectorName': row['connector_name'],
                'connectorType': row['connector_type'],
                'configuration': row['configuration'],
                'status': row['status'],
                'createdAt': row['created_at']
            }
            connectors.append(connector_data)
        
        return jsonify(connectors), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

@app.route('/api/connectors/<int:connector_id>/test', methods=['POST'])
def test_connector_connection(connector_id):
    """Test connector connection and update status"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get connector configuration
        cursor.execute("""
            SELECT id, connector_type, configuration, ci_id
            FROM tool_connectors 
            WHERE id = %s
        """, (connector_id,))
        
        connector = cursor.fetchone()
        if not connector:
            return jsonify({'error': 'Connector not found'}), 404
        
        connector_type = connector['connector_type']
        config = connector['configuration']
        
        # Test connection based on connector type
        test_result = test_connector_by_type(connector_type, config)
        
        # Update connector status based on test result
        new_status = 'active' if test_result['success'] else 'failed'
        cursor.execute("""
            UPDATE tool_connectors 
            SET status = %s
            WHERE id = %s
        """, (new_status, connector_id))
        conn.commit()
        
        return jsonify({
            'success': test_result['success'],
            'status': new_status,
            'message': test_result['message'],
            'details': test_result.get('details', {}),
            'testDuration': test_result.get('duration', 0)
        }), 200
        
    except Exception as e:
        # Mark connector as failed on exception
        if conn:
            try:
                cursor.execute("UPDATE tool_connectors SET status = 'failed' WHERE id = %s", (connector_id,))
                conn.commit()
            except:
                pass
        return jsonify({'error': str(e), 'success': False}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

def test_connector_by_type(connector_type, config):
    """Test connection for specific connector type"""
    import time
    start_time = time.time()
    
    try:
        if connector_type == 'SQL Server DB':
            return test_sql_server_connection(config, start_time)
        elif connector_type == 'Oracle DB':
            return test_oracle_connection(config, start_time)
        elif connector_type == 'Gnosis Document Repository':
            return test_gnosis_connection(config, start_time)
        elif connector_type == 'Jira':
            return test_jira_connection(config, start_time)
        elif connector_type == 'QTest':
            return test_qtest_connection(config, start_time)
        elif connector_type == 'ServiceNow':
            return test_servicenow_connection(config, start_time)
        else:
            return {
                'success': False,
                'message': f'Unknown connector type: {connector_type}',
                'duration': time.time() - start_time
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'Connection test failed: {str(e)}',
            'duration': time.time() - start_time
        }

def test_sql_server_connection(config, start_time):
    """Test SQL Server database connection"""
    import socket
    import time
    
    server = config.get('server', '')
    port = int(config.get('port', 1433))
    database = config.get('database', '')
    
    if not server or not database:
        return {
            'success': False,
            'message': 'Missing required configuration: server and database are required',
            'duration': time.time() - start_time
        }
    
    # Test network connectivity
    try:
        socket.setdefaulttimeout(5)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((server, port))
        sock.close()
        
        if result == 0:
            return {
                'success': True,
                'message': f'Successfully connected to SQL Server {server}:{port}',
                'details': {
                    'server': server,
                    'port': port,
                    'database': database,
                    'connectionType': 'network_test'
                },
                'duration': time.time() - start_time
            }
        else:
            return {
                'success': False,
                'message': f'Cannot connect to SQL Server {server}:{port} - server unreachable',
                'duration': time.time() - start_time
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'SQL Server connection test failed: {str(e)}',
            'duration': time.time() - start_time
        }

def test_oracle_connection(config, start_time):
    """Test Oracle database connection"""
    import socket
    import time
    
    server = config.get('server', '')
    port = int(config.get('port', 1521))
    service_name = config.get('service_name', config.get('database', ''))
    
    if not server or not service_name:
        return {
            'success': False,
            'message': 'Missing required configuration: server and service_name are required',
            'duration': time.time() - start_time
        }
    
    try:
        socket.setdefaulttimeout(5)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((server, port))
        sock.close()
        
        if result == 0:
            return {
                'success': True,
                'message': f'Successfully connected to Oracle {server}:{port}/{service_name}',
                'details': {
                    'server': server,
                    'port': port,
                    'serviceName': service_name,
                    'connectionType': 'network_test'
                },
                'duration': time.time() - start_time
            }
        else:
            return {
                'success': False,
                'message': f'Cannot connect to Oracle {server}:{port} - server unreachable',
                'duration': time.time() - start_time
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'Oracle connection test failed: {str(e)}',
            'duration': time.time() - start_time
        }

def test_gnosis_connection(config, start_time):
    """Test Gnosis Document Repository connection"""
    import urllib.request
    import urllib.error
    import time
    
    server = config.get('server', '')
    api_endpoint = config.get('api_endpoint', '/api/v2/documents')
    repository = config.get('repository', '')
    
    if not server:
        return {
            'success': False,
            'message': 'Missing required configuration: server is required',
            'duration': time.time() - start_time
        }
    
    # Construct test URL
    test_url = f"https://{server}{api_endpoint}"
    if not server.startswith('http'):
        test_url = f"https://{server}{api_endpoint}"
    
    try:
        # Test HTTP connectivity with timeout
        req = urllib.request.Request(test_url, headers={'User-Agent': 'CA-Audit-Agent/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            
            if status_code in [200, 401, 403]:  # 401/403 means server is reachable but needs auth
                return {
                    'success': True,
                    'message': f'Successfully connected to Gnosis server {server}',
                    'details': {
                        'server': server,
                        'endpoint': api_endpoint,
                        'repository': repository,
                        'httpStatus': status_code,
                        'connectionType': 'http_test'
                    },
                    'duration': time.time() - start_time
                }
            else:
                return {
                    'success': False,
                    'message': f'Gnosis server returned unexpected status: {status_code}',
                    'duration': time.time() - start_time
                }
    except urllib.error.URLError as e:
        return {
            'success': False,
            'message': f'Cannot connect to Gnosis server {server}: {str(e)}',
            'duration': time.time() - start_time
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Gnosis connection test failed: {str(e)}',
            'duration': time.time() - start_time
        }

def test_jira_connection(config, start_time):
    """Test Jira connection"""
    import urllib.request
    import urllib.error
    import time
    
    server = config.get('server', '')
    project_key = config.get('project_key', '')
    api_version = config.get('api_version', '3')
    
    if not server:
        return {
            'success': False,
            'message': 'Missing required configuration: server is required',
            'duration': time.time() - start_time
        }
    
    # Construct test URL
    test_url = f"https://{server}/rest/api/{api_version}/serverInfo"
    
    try:
        req = urllib.request.Request(test_url, headers={'User-Agent': 'CA-Audit-Agent/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            
            if status_code in [200, 401, 403]:
                return {
                    'success': True,
                    'message': f'Successfully connected to Jira server {server}',
                    'details': {
                        'server': server,
                        'projectKey': project_key,
                        'apiVersion': api_version,
                        'httpStatus': status_code,
                        'connectionType': 'http_test'
                    },
                    'duration': time.time() - start_time
                }
            else:
                return {
                    'success': False,
                    'message': f'Jira server returned unexpected status: {status_code}',
                    'duration': time.time() - start_time
                }
    except urllib.error.URLError as e:
        return {
            'success': False,
            'message': f'Cannot connect to Jira server {server}: {str(e)}',
            'duration': time.time() - start_time
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Jira connection test failed: {str(e)}',
            'duration': time.time() - start_time
        }

def test_qtest_connection(config, start_time):
    """Test QTest connection"""
    import urllib.request
    import urllib.error
    import time
    
    server = config.get('server', '')
    project_id = config.get('project_id', '')
    api_version = config.get('api_version', 'v3')
    
    if not server:
        return {
            'success': False,
            'message': 'Missing required configuration: server is required',
            'duration': time.time() - start_time
        }
    
    # Construct test URL
    test_url = f"https://{server}/api/{api_version}/projects/{project_id}" if project_id else f"https://{server}/api/{api_version}/projects"
    
    try:
        req = urllib.request.Request(test_url, headers={'User-Agent': 'CA-Audit-Agent/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            
            if status_code in [200, 401, 403]:
                return {
                    'success': True,
                    'message': f'Successfully connected to QTest server {server}',
                    'details': {
                        'server': server,
                        'projectId': project_id,
                        'apiVersion': api_version,
                        'httpStatus': status_code,
                        'connectionType': 'http_test'
                    },
                    'duration': time.time() - start_time
                }
            else:
                return {
                    'success': False,
                    'message': f'QTest server returned unexpected status: {status_code}',
                    'duration': time.time() - start_time
                }
    except urllib.error.URLError as e:
        return {
            'success': False,
            'message': f'Cannot connect to QTest server {server}: {str(e)}',
            'duration': time.time() - start_time
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'QTest connection test failed: {str(e)}',
            'duration': time.time() - start_time
        }

def test_servicenow_connection(config, start_time):
    """Test ServiceNow connection"""
    import urllib.request
    import urllib.error
    import time
    
    instance = config.get('instance', '')
    endpoint = config.get('endpoint', 'api/now/table/incident')
    version = config.get('version', 'v1')
    
    if not instance:
        return {
            'success': False,
            'message': 'Missing required configuration: instance is required',
            'duration': time.time() - start_time
        }
    
    # Construct test URL
    test_url = f"https://{instance}/{endpoint}"
    
    try:
        req = urllib.request.Request(test_url, headers={'User-Agent': 'CA-Audit-Agent/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            
            if status_code in [200, 401, 403]:
                return {
                    'success': True,
                    'message': f'Successfully connected to ServiceNow instance {instance}',
                    'details': {
                        'instance': instance,
                        'endpoint': endpoint,
                        'version': version,
                        'httpStatus': status_code,
                        'connectionType': 'http_test'
                    },
                    'duration': time.time() - start_time
                }
            else:
                return {
                    'success': False,
                    'message': f'ServiceNow instance returned unexpected status: {status_code}',
                    'duration': time.time() - start_time
                }
    except urllib.error.URLError as e:
        return {
            'success': False,
            'message': f'Cannot connect to ServiceNow instance {instance}: {str(e)}',
            'duration': time.time() - start_time
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'ServiceNow connection test failed: {str(e)}',
            'duration': time.time() - start_time
        }

@app.route('/api/database/health', methods=['GET'])
def database_health_check():
    """Check database connectivity and status"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'status': 'error',
                'connection': False,
                'message': 'Failed to connect to database'
            }), 500
        
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT NOW() as current_time")
        result = cursor.fetchone()
        
        # Get table count
        cursor.execute("""
            SELECT COUNT(*) as table_count 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        table_count = cursor.fetchone()[0]
        
        # Get record counts for main tables
        cursor.execute("SELECT COUNT(*) FROM applications")
        apps_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tool_connectors")
        connectors_count = cursor.fetchone()[0]
        
        return jsonify({
            'status': 'healthy',
            'connection': True,
            'message': 'Database connection successful',
            'details': {
                'currentTime': str(result[0]),
                'tableCount': table_count,
                'applicationCount': apps_count,
                'connectorCount': connectors_count
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'connection': False,
            'message': str(e)
        }), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == '__main__':
    print("🐍 Starting Simple Flask API server...")
    print("📡 CORS enabled for React frontend at http://localhost:5000")
    print("🔗 Flask backend running at http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)