#!/usr/bin/env python3
"""
Simple Flask API server for audit data collection application
Clean Flask backend with CORS enabled for React frontend
"""

import os
import json
import pandas as pd
import tempfile
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from werkzeug.utils import secure_filename
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import traceback
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import shutil
import time

# Load environment variables
load_dotenv()

# Initialize Langchain OpenAI
llm = ChatOpenAI(
    model=
    "gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
    api_key=os.getenv('OPENAI_API_KEY'),
    temperature=0.1,
    max_tokens=2000)

app = Flask(__name__)
CORS(
    app,
    origins=[
        "http://localhost:5000", "http://0.0.0.0:5000",
        "https://7148f2c9-02b0-4430-8db4-b17d1ed51f18-00-1f4bz4pbor6xh.riker.replit.dev",
        "http://7148f2c9-02b0-4430-8db4-b17d1ed51f18-00-1f4bz4pbor6xh.riker.replit.dev"
    ],
    supports_credentials=True)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_document_file(filename):
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in DOCUMENT_EXTENSIONS


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
            conn = psycopg2.connect(host=os.getenv('PGHOST', 'localhost'),
                                    database=os.getenv('PGDATABASE',
                                                       'postgres'),
                                    user=os.getenv('PGUSER', 'postgres'),
                                    password=os.getenv('PGPASSWORD', ''),
                                    port=os.getenv('PGPORT', '5432'))
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
                   start_date, end_date, enable_followup_questions, created_at, status
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
                'enableFollowupQuestions': row['enable_followup_questions']
                or False,
                'createdAt': row['created_at'],
                'status': row.get('status', 'In Progress')
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

        cursor.execute(
            """
            INSERT INTO applications (name, audit_name, ci_id, start_date, end_date, enable_followup_questions)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, name, audit_name, ci_id, start_date, end_date, enable_followup_questions, created_at
        """,
            (
                data.get('name') or
                data['auditName'],  # Use name if provided, otherwise auditName
                data['auditName'],
                data['ciId'],
                data.get('startDate') or data.get('auditDateFrom'),
                data.get('endDate') or data.get('auditDateTo'),
                enable_followup))

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
        cursor.execute(
            """
            SELECT id, name, audit_name, ci_id, 
                   start_date, end_date, enable_followup_questions, created_at,
                   status
            FROM applications 
            WHERE id = %s
        """, (application_id, ))

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
            'enableFollowupQuestions': row['enable_followup_questions']
            or False,
            'createdAt': row['created_at'],
            'status': row.get('status', 'In Progress')
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
        cursor.execute("SELECT id FROM applications WHERE id = %s",
                       (application_id, ))
        if not cursor.fetchone():
            return jsonify({'error': 'Application not found'}), 404

        # Extract follow-up questions setting
        settings = data.get('settings', {})
        enable_followup = settings.get('enableFollowUpQuestions', False)

        # Handle different update scenarios
        if 'status' in data and len(data) == 1:
            # Status-only update
            cursor.execute(
                """
                UPDATE applications 
                SET status = %s
                WHERE id = %s
                RETURNING id, name, audit_name, ci_id, start_date, end_date, enable_followup_questions, created_at, status
            """, (data['status'], application_id))
        else:
            # Full application update
            cursor.execute(
                """
                UPDATE applications 
                SET name = %s, audit_name = %s, ci_id = %s, start_date = %s, end_date = %s, enable_followup_questions = %s
                WHERE id = %s
                RETURNING id, name, audit_name, ci_id, start_date, end_date, enable_followup_questions, created_at, status
            """, (data.get('name') or data['auditName'], data['auditName'],
                  data['ciId'], data.get('startDate')
                  or data.get('auditDateFrom'), data.get('endDate')
                  or data.get('auditDateTo'), enable_followup, application_id))

        row = cursor.fetchone()
        conn.commit()

        app_data = {
            'id': row['id'],
            'name': row['name'],
            'auditName': row['audit_name'],
            'ciId': row['ci_id'],
            'auditDateFrom': row['start_date'],
            'auditDateTo': row['end_date'],
            'enableFollowupQuestions': row['enable_followup_questions'],
            'createdAt': row['created_at'],
            'status': row.get('status', 'In Progress')
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
        cursor.execute(
            """
            SELECT name, audit_name, ci_id
            FROM applications 
            WHERE id = %s
        """, (application_id, ))

        application = cursor.fetchone()
        if not application:
            return jsonify({'error': 'Application not found'}), 404

        # Start transaction for complete cleanup
        cursor.execute("BEGIN;")

        try:
            # Delete agent executions
            cursor.execute(
                "DELETE FROM agent_executions WHERE application_id = %s",
                (application_id, ))

            # Delete question analyses
            cursor.execute(
                "DELETE FROM question_analyses WHERE application_id = %s",
                (application_id, ))

            # Delete data collection sessions
            cursor.execute(
                "DELETE FROM data_collection_sessions WHERE application_id = %s",
                (application_id, ))

            # Delete data requests
            cursor.execute(
                "DELETE FROM data_requests WHERE application_id = %s",
                (application_id, ))

            # Delete the application
            cursor.execute("DELETE FROM applications WHERE id = %s",
                           (application_id, ))

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
                'message':
                f'Application "{application["audit_name"]}" and all associated data deleted successfully',
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
        return jsonify({'error':
                        f'Failed to delete application: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()


# Data requests API
@app.route('/api/data-requests/application/<int:application_id>',
           methods=['GET'])
def get_data_requests(application_id):
    """Get data requests for application"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT id, application_id, file_name, file_size, file_type, 
                   questions, total_questions, categories, subcategories, 
                   column_mappings, uploaded_at
            FROM data_requests 
            WHERE application_id = %s
            ORDER BY uploaded_at DESC
        """, (application_id, ))

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
            return jsonify({
                'error':
                'Invalid file format. Only .xlsx and .xls files are allowed'
            }), 400

        # Save file temporarily
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                 f"temp_{filename}")
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
        return jsonify({'error': f'Error reading Excel file: {str(e)}'}), 500


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
            return jsonify({
                'error':
                'Invalid file format. Only .xlsx and .xls files are allowed'
            }), 400

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
        cursor.execute("SELECT audit_name FROM applications WHERE id = %s",
                       (application_id, ))
        app_row = cursor.fetchone()

        if not app_row:
            return jsonify({'error': 'Application not found'}), 404

        # Create audit folder and save file
        audit_folder = create_audit_folder(application_id,
                                           app_row['audit_name'])
        file_path, unique_filename = save_uploaded_file(
            file, audit_folder, file_type)

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
                    'id':
                    f"Q{index + 1}",
                    'questionNumber':
                    safe_str(
                        row.get(column_mappings.get('questionNumber', ''),
                                f"Q{index + 1}")),
                    'process':
                    safe_str(row.get(column_mappings.get('process', ''), '')),
                    'subProcess':
                    safe_str(row.get(column_mappings.get('subProcess', ''),
                                     '')),
                    'question':
                    safe_str(row.get(column_mappings.get('question', ''), ''))
                }
                questions.append(question_data)

                # Collect categories and subcategories
                if question_data['process'] and question_data['process'] != '':
                    categories.add(question_data['process'])
                if question_data['subProcess'] and question_data[
                        'subProcess'] != '':
                    subcategories.add(question_data['subProcess'])

            # Save to database

            # Insert data request record
            cursor.execute(
                """
                INSERT INTO data_requests 
                (application_id, file_name, file_size, file_type, questions, 
                 total_questions, categories, subcategories, column_mappings, file_path, uploaded_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, file_name, total_questions
            """,
                (application_id, unique_filename, os.path.getsize(file_path),
                 file_type, json.dumps(questions), len(questions),
                 json.dumps(list(categories)), json.dumps(list(subcategories)),
                 json.dumps(column_mappings), file_path, datetime.now()))

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
        return jsonify({'error':
                        f'Error processing Excel file: {str(e)}'}), 500


# Question analysis API endpoints using OpenAI
@app.route('/api/questions/analyze', methods=['POST'])
def analyze_questions_with_ai():
    """Analyze questions using OpenAI to determine tools and prompts"""
    try:
        data = request.get_json()
        application_id = data.get('applicationId')
        questions = data.get('questions', [])

        if not application_id or not questions:
            return jsonify(
                {'error': 'Application ID and questions are required'}), 400

        # Use Langchain with OpenAI for intelligent question analysis
        analyses = []

        # Create Langchain prompt template with multi-tool selection capability
        system_template = """You are an expert audit data collection specialist. Analyze each audit question and intelligently determine the most appropriate tool(s) based on the question content and context.

IMPORTANT: You can select MULTIPLE tools for a single question when comprehensive data collection is needed.

TOOL SELECTION GUIDELINES:
- sql_server: Database queries, user data, system logs, transactions, authentication records, access controls
- oracle_db: Enterprise database systems, financial data, ERP systems, large-scale data analysis
- gnosis: Document searches, policies, procedures, manuals, compliance documents, knowledge base
- jira: Project tracking, issue management, bug reports, development workflow, change requests  
- qtest: Quality assurance, test cases, test results, defect tracking, testing documentation
- service_now: IT service management, incidents, service requests, change management, ITSM processes

MULTI-TOOL SELECTION EXAMPLES:
- "Review security incident response process" → ["gnosis", "jira", "service_now"] (policies + tickets + incidents)
- "Audit user access and permissions" → ["sql_server", "oracle_db"] (multiple database systems)
- "Check compliance documentation and implementation" → ["gnosis", "jira"] (docs + implementation tracking)
- "Review testing processes and results" → ["qtest", "jira"] (test data + project tracking)

ANALYSIS APPROACH:
1. Read the question carefully and identify key terms
2. Consider if multiple data sources would provide comprehensive coverage
3. Select one or more tools that together provide complete answer
4. Create specific, actionable prompts for data collection agents
5. Provide clear reasoning for tool selection

Respond in JSON format only:
{{
  "toolSuggestion": "single_tool_id OR array_of_tool_ids like ['tool1', 'tool2']",
  "aiPrompt": "Create comprehensive, actionable instructions for an AI data collection agent. Include specific search criteria, expected data types, analysis requirements, and deliverable format. Make it detailed enough for autonomous execution.",
  "connectorReason": "Clear explanation why these tool(s) are the best choice for this specific question",
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
                    question=question.get('question', ''))

                # Get AI analysis using Langchain with JSON parsing
                response = llm.invoke(formatted_prompt)

                # Parse the JSON response with better error handling
                try:
                    ai_analysis = json.loads(response.content)

                    # Handle both single and multiple tool suggestions
                    valid_tools = [
                        'sql_server', 'oracle_db', 'gnosis', 'jira', 'qtest',
                        'service_now'
                    ]
                    tool_suggestion = ai_analysis.get('toolSuggestion')

                    # Check if it's a valid single tool or array of tools
                    if isinstance(tool_suggestion, list):
                        # Multiple tools - validate each one
                        validated_tools = [
                            tool for tool in tool_suggestion
                            if tool in valid_tools
                        ]
                        if not validated_tools:
                            # If no valid tools in the array, fallback to content analysis
                            tool_suggestion = None
                        else:
                            ai_analysis['toolSuggestion'] = validated_tools
                    elif tool_suggestion not in valid_tools:
                        # Single tool but invalid - fallback to content analysis
                        tool_suggestion = None

                    if tool_suggestion is None:
                        # If invalid tool, try to map based on question content
                        question_text = question.get('question', '').lower()
                        if any(term in question_text for term in [
                                'database', 'user', 'access', 'login',
                                'authentication'
                        ]):
                            ai_analysis['toolSuggestion'] = 'sql_server'
                        elif any(term in question_text for term in [
                                'document', 'policy', 'procedure', 'manual',
                                'compliance'
                        ]):
                            ai_analysis['toolSuggestion'] = 'gnosis'
                        elif any(term in question_text for term in
                                 ['test', 'quality', 'defect', 'bug', 'qa']):
                            ai_analysis['toolSuggestion'] = 'qtest'
                        elif any(term in question_text for term in [
                                'incident', 'service', 'request', 'itsm',
                                'change'
                        ]):
                            ai_analysis['toolSuggestion'] = 'service_now'
                        elif any(
                                term in question_text for term in
                            ['project', 'issue', 'development', 'workflow']):
                            ai_analysis['toolSuggestion'] = 'jira'
                        else:
                            ai_analysis[
                                'toolSuggestion'] = 'sql_server'  # Default fallback

                except json.JSONDecodeError as je:
                    print(
                        f"JSON parsing error for question {question.get('id', '')}: {je}"
                    )
                    print(f"Raw response: {response.content}")

                    # Intelligent fallback based on question content
                    question_text = question.get('question', '').lower()
                    if any(term in question_text for term in [
                            'database', 'user', 'access', 'login',
                            'authentication', 'data', 'record'
                    ]):
                        tool_suggestion = 'sql_server'
                    elif any(term in question_text for term in [
                            'document', 'policy', 'procedure', 'manual',
                            'compliance', 'guideline'
                    ]):
                        tool_suggestion = 'gnosis'
                    elif any(
                            term in question_text for term in
                        ['test', 'quality', 'defect', 'bug', 'qa', 'testing']):
                        tool_suggestion = 'qtest'
                    elif any(term in question_text for term in [
                            'incident', 'service', 'request', 'itsm', 'change',
                            'ticket'
                    ]):
                        tool_suggestion = 'service_now'
                    elif any(term in question_text for term in [
                            'project', 'issue', 'development', 'workflow',
                            'jira'
                    ]):
                        tool_suggestion = 'jira'
                    elif any(term in question_text for term in
                             ['oracle', 'erp', 'financial', 'enterprise']):
                        tool_suggestion = 'oracle_db'
                    else:
                        tool_suggestion = 'sql_server'

                    ai_analysis = {
                        'category':
                        question.get('process', 'General'),
                        'subcategory':
                        question.get('subProcess', 'Unknown'),
                        'toolSuggestion':
                        tool_suggestion,
                        'aiPrompt':
                        f"Execute comprehensive data collection for audit question: {question.get('question', '')}. Search {tool_suggestion} system for relevant records, analyze data patterns, and compile detailed findings with specific evidence and metrics.",
                        'connectorReason':
                        f'Selected {tool_suggestion} based on question content analysis'
                    }

                # Handle connector assignment for both single and multiple tools
                tool_suggestion = ai_analysis.get('toolSuggestion',
                                                  'sql_server')
                connector_to_use = tool_suggestion if isinstance(
                    tool_suggestion, list) else tool_suggestion

                analysis = {
                    'questionId':
                    question.get('id', ''),
                    'originalQuestion':
                    question.get('question', ''),
                    'category':
                    ai_analysis.get('category', question.get('process', '')),
                    'subcategory':
                    ai_analysis.get('subcategory',
                                    question.get('subProcess', '')),
                    'aiPrompt':
                    ai_analysis.get('aiPrompt', ''),
                    'toolSuggestion':
                    tool_suggestion,
                    'connectorReason':
                    ai_analysis.get('connectorReason', ''),
                    'connectorToUse':
                    connector_to_use
                }

                analyses.append(analysis)

            except Exception as e:
                print(
                    f"Error analyzing question {question.get('id', '')}: {e}")
                # Fallback analysis
                analyses.append({
                    'questionId':
                    question.get('id', ''),
                    'originalQuestion':
                    question.get('question', ''),
                    'category':
                    question.get('process', ''),
                    'subcategory':
                    question.get('subProcess', ''),
                    'aiPrompt':
                    f"Execute comprehensive audit data collection: {question.get('question', '')}. Access document repository, search for relevant policies and procedures, extract key findings, and provide detailed compliance assessment.",
                    'toolSuggestion':
                    'gnosis',  # Default to document repository for unknown questions
                    'connectorReason':
                    'Fallback selection - review question for optimal tool choice',
                    'connectorToUse':
                    'gnosis'
                })

        return jsonify({'analyses': analyses, 'total': len(analyses)}), 200

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
        cursor.execute(
            """
            SELECT question_id, original_question, category, subcategory,
                   ai_prompt, tool_suggestion, connector_reason, connector_to_use
            FROM question_analyses 
            WHERE application_id = %s
            ORDER BY question_id
        """, (application_id, ))

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
        cursor.execute(
            """
            SELECT questions FROM data_requests 
            WHERE application_id = %s AND file_type = 'primary'
            ORDER BY uploaded_at DESC LIMIT 1
        """, (application_id, ))

        result = cursor.fetchone()
        if not result:
            return jsonify(
                {'error': 'No questions found for this application'}), 404

        questions = result['questions']
        if isinstance(questions, str):
            questions = json.loads(questions)

        # Mock AI analysis - in real implementation, this would use OpenAI
        analyzed_questions = []
        for q in questions:
            analyzed_q = {
                'questionId':
                q.get('id',
                      q.get('questionNumber',
                            f'Q{len(analyzed_questions)+1}')),
                'originalQuestion':
                q.get('question', ''),
                'category':
                q.get('process', 'General'),
                'subcategory':
                q.get('subProcess', ''),
                'aiPrompt':
                f"Analyze the following audit question and provide detailed guidance: {q.get('question', '')}",
                'toolSuggestion':
                'SQL Server DB',  # Updated to new format
                'connectorReason':
                'This question requires database analysis to verify compliance.',
                'connectorToUse':
                'SQL Server DB'  # Updated to new format
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
        cursor.execute(
            "DELETE FROM question_analyses WHERE application_id = %s",
            (application_id, ))

        # Insert new analyses with unique identifiers
        for idx, analysis in enumerate(analyses):
            # Create unique question_id by combining original id with index
            unique_question_id = f"{analysis.get('questionId', analysis.get('id', f'Q{idx+1}'))}-{idx}"

            cursor.execute(
                """
                INSERT INTO question_analyses 
                (application_id, question_id, original_question, category, subcategory,
                 ai_prompt, tool_suggestion, connector_reason, connector_to_use)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (application_id, unique_question_id,
                  analysis.get('originalQuestion', ''),
                  analysis.get('category', ''), analysis.get(
                      'subcategory', ''), analysis.get(
                          'aiPrompt', ''), analysis.get('toolSuggestion', ''),
                  analysis.get('connectorReason',
                               ''), analysis.get('connectorToUse', '')))

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


# Mock AGent Execution API
@app.route('/api/agent/execute', methods=['POST'])
def execute_agent():
    """Execute AI agents to collect data using mock connectors for demo"""
    try:
        data = request.get_json()
        application_id = data.get('applicationId')

        if not application_id:
            return jsonify({'error': 'Application ID is required'}), 400

        # Import demo components
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'demo'))

        try:
            from mock_agent_executor import demo_agent
        except ImportError as e:
            return jsonify(
                {'error': f'Demo components not available: {str(e)}'}), 500

        # Get question analyses for this application
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get all question analyses
        cursor.execute(
            """
            SELECT qa.*, app.audit_name, app.ci_id
            FROM question_analyses qa
            JOIN applications app ON qa.application_id = app.id
            WHERE qa.application_id = %s
            ORDER BY qa.created_at
        """, (application_id, ))

        analyses = cursor.fetchall()

        if not analyses:
            return jsonify(
                {'error':
                 'No question analyses found for this application'}), 404

        # Convert database results to format expected by mock agent
        question_analyses = []
        for analysis in analyses:
            # Handle both single and multiple tool suggestions
            tool_suggestion = analysis['tool_suggestion']
            if isinstance(tool_suggestion, str):
                try:
                    # Try to parse as JSON array
                    if tool_suggestion.startswith('['):
                        tool_suggestion = json.loads(tool_suggestion)
                    # If it's quoted, remove quotes
                    elif tool_suggestion.startswith(
                            '"') and tool_suggestion.endswith('"'):
                        tool_suggestion = tool_suggestion[1:-1]
                except json.JSONDecodeError:
                    pass  # Keep as string if not valid JSON

            question_analysis = {
                'questionId': analysis['question_id'],
                'originalQuestion': analysis['original_question'],
                'toolSuggestion': tool_suggestion,
                'aiPrompt': analysis['ai_prompt'],
                'category': analysis['category'],
                'subcategory': analysis['subcategory'],
                'connectorReason': analysis['connector_reason']
            }
            question_analyses.append(question_analysis)

        # Execute mock agent data collection
        execution_results = []

        for question_analysis in question_analyses:
            # Execute data collection using mock connectors
            execution_result = demo_agent.execute_data_collection(
                question_analysis)

            # Store or update execution result in database
            cursor.execute(
                """
                INSERT INTO agent_executions 
                (application_id, question_id, tool_used, execution_time, 
                 data_collected, findings, status, confidence, risk_level, compliance_status, executed_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (application_id, question_id) 
                DO UPDATE SET
                    tool_used = EXCLUDED.tool_used,
                    execution_time = EXCLUDED.execution_time,
                    data_collected = EXCLUDED.data_collected,
                    findings = EXCLUDED.findings,
                    status = EXCLUDED.status,
                    confidence = EXCLUDED.confidence,
                    risk_level = EXCLUDED.risk_level,
                    compliance_status = EXCLUDED.compliance_status,
                    executed_at = EXCLUDED.executed_at
                RETURNING id
            """,
                (application_id, execution_result['questionId'],
                 json.dumps(execution_result['toolsUsed']),
                 execution_result['duration'], execution_result['dataPoints'],
                 json.dumps({
                     'findings': execution_result['findings'],
                     'analysis': execution_result['analysis'],
                     'collectedData': {
                         k: len(v) if isinstance(v, list) else 1
                         for k, v in execution_result['collectedData'].items()
                     }
                 }), execution_result['status'],
                 execution_result['analysis']['confidence'],
                 execution_result['riskLevel'],
                 execution_result['complianceStatus'], datetime.now()))

            execution_id = cursor.fetchone()['id']
            execution_result['databaseId'] = execution_id

            execution_results.append(execution_result)

        conn.commit()

        # Generate summary statistics
        total_data_points = sum(result['dataPoints']
                                for result in execution_results)
        avg_confidence = sum(
            result['analysis']['confidence']
            for result in execution_results) / len(execution_results)
        risk_distribution = {}
        for result in execution_results:
            risk = result['riskLevel']
            risk_distribution[risk] = risk_distribution.get(risk, 0) + 1

        return jsonify({
            'message':
            f'Mock agent execution completed for {len(execution_results)} questions',
            'totalExecutions': len(execution_results),
            'totalDataPoints': total_data_points,
            'averageConfidence': round(avg_confidence, 3),
            'riskDistribution': risk_distribution,
            'executions': execution_results,
            'summary': {
                'toolsUsed':
                list(
                    set(tool for result in execution_results
                        for tool in result['toolsUsed'])),
                'avgExecutionTime':
                round(
                    sum(result['duration'] for result in execution_results) /
                    len(execution_results), 2),
                'complianceOverview': {
                    'compliant':
                    len([
                        r for r in execution_results
                        if r['complianceStatus'] == 'Compliant'
                    ]),
                    'partiallyCompliant':
                    len([
                        r for r in execution_results
                        if r['complianceStatus'] == 'Partially Compliant'
                    ]),
                    'nonCompliant':
                    len([
                        r for r in execution_results
                        if r['complianceStatus'] == 'Non-Compliant'
                    ])
                }
            }
        }), 200

    except Exception as e:
        if 'conn' in locals() and conn:
            conn.rollback()
        return jsonify({'error':
                        f'Error executing mock agents: {str(e)}'}), 500

    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()


# DB Health Check API
@app.route('/api/database/health', methods=['GET'])
def database_health():
    """Database connectivity health check"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'status':
                'error',
                'message':
                'Unable to connect to database',
                'database_url_present':
                bool(os.getenv('DATABASE_URL')),
                'error_details':
                'Connection failed'
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


# File-Based Agent Execution API
@app.route('/api/agents/execute', methods=['POST'])
def execute_agent_request():
    """Execute AI agent for data collection using file-based connectors"""
    try:
        from data_connectors import DataConnectorFactory

        data = request.get_json()
        application_id = data.get('applicationId')
        question_id = data.get('questionId')
        prompt = data.get('prompt', '')
        tool_type = data.get('toolType', 'sql_server')
        connector_id = data.get('connectorId')

        if not all([application_id, question_id, prompt]):
            return jsonify({
                'error':
                'Missing required fields: applicationId, questionId, prompt'
            }), 400

        # Get application and question details
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get application CI ID for data path
        cursor.execute(
            """
            SELECT app.ci_id, qa.original_question, qa.category, qa.subcategory 
            FROM applications app
            JOIN question_analyses qa ON app.id = qa.application_id
            WHERE app.id = %s AND qa.question_id = %s
        """, (application_id, question_id))

        result = cursor.fetchone()
        if not result:
            return jsonify({'error': 'Application or question not found'}), 404

        ci_id = result['ci_id']
        original_question = result['original_question']
        category = result['category']
        subcategory = result['subcategory']

        # Configuration for tools data path - using server/tools folder
        tools_path = os.path.join(os.path.dirname(__file__), 'tools')

        # Ensure the path exists
        if not os.path.exists(os.path.join(tools_path, ci_id)):
            return jsonify({
                'error':
                f'Tools data folder not found for CI {ci_id}. Expected path: {tools_path}/{ci_id}',
                'suggestion':
                'Please ensure data files are properly organized in the tools folder structure'
            }), 404

        try:
            # Create data connector factory
            connector_factory = DataConnectorFactory(tools_path, ci_id, llm)

            # Execute tool query using file-based data
            start_time = datetime.now()
            execution_result = connector_factory.execute_tool_query(
                tool_type, original_question)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Check if execution had errors
            if 'error' in execution_result:
                # Handle file not found or connector issues with fallback
                fallback_result = {
                    'analysis': {
                        'executiveSummary':
                        f'Data collection attempted for: {original_question}. {execution_result["error"]}',
                        'findings':
                        [f'Data source issue: {execution_result["error"]}'],
                        'riskLevel':
                        'Medium',
                        'complianceStatus':
                        'Review Required',
                        'dataPoints':
                        0,
                        'keyInsights': ['Data source configuration needed'],
                        'recommendations':
                        ['Verify data file paths and structure']
                    },
                    'dataPoints': 0,
                    'duration': duration,
                    'status': 'completed_with_issues'
                }
                execution_result = fallback_result
            else:
                # Add duration and status to successful results
                execution_result['duration'] = duration
                execution_result['status'] = 'completed'

            # Store execution result in database
            cursor.execute(
                """
                INSERT INTO agent_executions (
                    application_id, question_id, tool_type, connector_id, prompt, 
                    result, status, execution_details, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                RETURNING id
            """,
                (application_id, question_id, tool_type, connector_id, prompt,
                 json.dumps(execution_result),
                 execution_result.get('status', 'completed'),
                 json.dumps({
                     'findings':
                     execution_result.get('analysis', {}).get('findings', []),
                     'dataPoints':
                     execution_result.get('dataPoints', 0),
                     'duration':
                     execution_result.get('duration', 0),
                     'toolUsed':
                     tool_type,
                     'dataSource':
                     f'{tools_path}/{ci_id}/{tool_type.replace("_", " ").title()}'
                 })))

            execution_id = cursor.fetchone()['id']
            conn.commit()

            # Return response in expected format
            analysis = execution_result.get('analysis', {})
            return jsonify({
                'executionId':
                execution_id,
                'status':
                execution_result.get('status', 'completed'),
                'findings':
                analysis.get('findings', []),
                'analysis': {
                    'executiveSummary':
                    analysis.get('executiveSummary',
                                 'Data collection completed'),
                    'riskLevel':
                    analysis.get('riskLevel', 'Low'),
                    'complianceStatus':
                    analysis.get('complianceStatus', 'Compliant'),
                    'totalDataPoints':
                    execution_result.get('dataPoints', 0)
                },
                'dataPoints':
                execution_result.get('dataPoints', 0),
                'collectedData':
                execution_result.get('rawData', {}),
                'duration':
                execution_result.get('duration', 0),
                'timestamp':
                end_time.isoformat(),
                'dataSource':
                f'{tool_type} files from CI {ci_id}'
            }), 200

        except Exception as connector_error:
            print(f"Connector error: {connector_error}")
            # Fallback to basic response if connector fails
            return jsonify({
                'executionId':
                f"fallback_{question_id}_{int(datetime.now().timestamp())}",
                'status':
                'completed_with_issues',
                'findings': [{
                    'tool':
                    tool_type,
                    'finding':
                    f'Data collection attempted for: {original_question}',
                    'severity':
                    'Warning',
                    'details':
                    f'Connector issue: {str(connector_error)}'
                }],
                'analysis': {
                    'executiveSummary':
                    f'Data collection attempted for question: {original_question}. Technical issue encountered with {tool_type} connector.',
                    'riskLevel': 'Medium',
                    'complianceStatus': 'Review Required',
                    'totalDataPoints': 0
                },
                'dataPoints':
                0,
                'duration':
                1.0,
                'timestamp':
                datetime.now().isoformat(),
                'dataSource':
                f'Connector error for {tool_type}'
            }), 200

    except Exception as e:
        print(f"Error in execute_agent: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals() and conn:
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
        cursor.execute(
            """
            SELECT ae.*, tc.name as connector_name
            FROM agent_executions ae
            LEFT JOIN tool_connectors tc ON ae.connector_id = tc.id
            WHERE ae.application_id = %s
            ORDER BY ae.created_at DESC
        """, (application_id, ))

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
        cursor.execute("SELECT id FROM applications WHERE ci_id = %s LIMIT 1",
                       (data.get('ciId'), ))
        app_row = cursor.fetchone()

        if not app_row:
            return jsonify({
                'error':
                f'No application found for CI ID: {data.get("ciId")}'
            }), 404

        application_id = app_row['id']

        # Get connector name from data, or generate default
        connector_name = data.get('connectorName')
        if not connector_name:
            connector_name = f"{data.get('connectorType', 'Unknown')} - {application_id}"

        # Insert tool connector
        cursor.execute(
            """
            INSERT INTO tool_connectors (application_id, ci_id, connector_name, connector_type, configuration, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, application_id, ci_id, connector_name, connector_type, configuration, status, created_at
        """, (application_id, data.get('ciId'), connector_name,
              data.get('connectorType'),
              json.dumps(data.get('configuration',
                                  {})), data.get('status', 'pending')))

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


@app.route('/api/questions/save-answer', methods=['POST'])
def save_question_answer():
    """Save AI agent execution results as question answers"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        application_id = data.get('applicationId')
        question_id = data.get('questionId')
        answer = data.get('answer', '')
        findings = data.get('findings', '[]')
        risk_level = data.get('riskLevel', 'Low')
        compliance_status = data.get('complianceStatus', 'Compliant')
        data_points = data.get('dataPoints', 0)
        execution_details = data.get('executionDetails', '{}')

        if not all([application_id, question_id]):
            return jsonify({
                'error':
                'Missing required fields: applicationId, questionId'
            }), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Check if answer already exists
        cursor.execute(
            """
            SELECT id FROM question_answers 
            WHERE application_id = %s AND question_id = %s
        """, (application_id, question_id))

        existing = cursor.fetchone()

        if existing:
            # Update existing answer
            cursor.execute(
                """
                UPDATE question_answers 
                SET answer = %s, findings = %s, risk_level = %s, compliance_status = %s,
                    data_points = %s, execution_details = %s, updated_at = NOW()
                WHERE application_id = %s AND question_id = %s
                RETURNING id
            """, (answer, findings, risk_level, compliance_status, data_points,
                  execution_details, application_id, question_id))
        else:
            # Insert new answer
            cursor.execute(
                """
                INSERT INTO question_answers (
                    application_id, question_id, answer, findings, risk_level,
                    compliance_status, data_points, execution_details, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING id
            """, (application_id, question_id, answer, findings, risk_level,
                  compliance_status, data_points, execution_details))

        result = cursor.fetchone()
        conn.commit()

        return jsonify({
            'id': result['id'],
            'message': 'Answer saved successfully',
            'questionId': question_id,
            'saved_at': datetime.now().isoformat()
        }), 200

    except Exception as e:
        if 'conn' in locals() and conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()


@app.route('/api/questions/answers/<int:application_id>', methods=['GET'])
def get_question_answers(application_id):
    """Get all saved answers for an application"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # First get data from agent_executions (Step 4 execution results)
        cursor.execute(
            """
            SELECT question_id, result, tool_used, created_at, execution_details
            FROM agent_executions 
            WHERE application_id = %s
        """, (application_id, ))
        
        agent_results = {row['question_id']: row for row in cursor.fetchall()}
        
        # Then get data from question_answers (Step 5 saved answers)
        cursor.execute(
            """
            SELECT question_id, answer, findings, risk_level, compliance_status, 
                   data_points, execution_details, created_at, updated_at
            FROM question_answers 
            WHERE application_id = %s
        """, (application_id, ))

        answer_results = {row['question_id']: row for row in cursor.fetchall()}
        
        # Combine both data sources, prioritizing saved answers over agent executions
        answers = []
        all_question_ids = set(agent_results.keys()) | set(answer_results.keys())
        
        for question_id in all_question_ids:
            agent_data = agent_results.get(question_id)
            answer_data = answer_results.get(question_id)
            
            # Parse agent result JSON if available
            result_data = {}
            if agent_data and agent_data['result']:
                try:
                    result_data = json.loads(agent_data['result']) if isinstance(agent_data['result'], str) else agent_data['result']
                except:
                    result_data = {}
            
            # Combine data with preference for manually saved answers
            combined_answer = {
                'questionId': question_id,
                'answer': '',
                'findings': [],
                'riskLevel': 'Low',
                'complianceStatus': 'Compliant',
                'dataPoints': 0,
                'executionDetails': {},
                'confidence': 0,
                'toolUsed': 'Unknown',
                'createdAt': None
            }
            
            # Fill from agent execution data first
            if agent_data:
                combined_answer.update({
                    'answer': result_data.get('analysis', {}).get('executiveSummary', ''),
                    'findings': result_data.get('findings', []),
                    'riskLevel': result_data.get('riskLevel', 'Low'),
                    'complianceStatus': result_data.get('complianceStatus', 'Compliant'),
                    'dataPoints': result_data.get('dataPoints', 0),
                    'confidence': result_data.get('analysis', {}).get('confidence', 0),
                    'toolUsed': agent_data['tool_used'] or 'Unknown',
                    'executionDetails': agent_data.get('execution_details', {}),
                    'createdAt': agent_data['created_at'].isoformat() if agent_data['created_at'] else None
                })
            
            # Override with manually saved answer data if available
            if answer_data:
                combined_answer.update({
                    'answer': answer_data['answer'] or combined_answer['answer'],
                    'findings': answer_data['findings'] or combined_answer['findings'],
                    'riskLevel': answer_data['risk_level'] or combined_answer['riskLevel'],
                    'complianceStatus': answer_data['compliance_status'] or combined_answer['complianceStatus'],
                    'dataPoints': answer_data['data_points'] or combined_answer['dataPoints'],
                    'executionDetails': answer_data['execution_details'] or combined_answer['executionDetails'],
                    'createdAt': answer_data['updated_at'].isoformat() if answer_data['updated_at'] else combined_answer['createdAt']
                })
            
            answers.append(combined_answer)

        return jsonify(answers), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()


@app.route('/api/applications/<int:application_id>/download-excel',
           methods=['GET'])
def download_excel_with_answers(application_id):
    """Generate and download Excel file with questions and populated answers"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get application details
        cursor.execute(
            "SELECT name, audit_name FROM applications WHERE id = %s",
            (application_id, ))
        app_data = cursor.fetchone()
        if not app_data:
            return jsonify({'error': 'Application not found'}), 404

        # Get question analyses
        cursor.execute(
            """
            SELECT id, original_question, category, subcategory, tool_suggestion
            FROM question_analyses 
            WHERE application_id = %s
            ORDER BY id
        """, (application_id, ))

        analyses = cursor.fetchall()

        # Get saved answers
        cursor.execute(
            """
            SELECT question_id, answer, risk_level, compliance_status, data_points
            FROM question_answers 
            WHERE application_id = %s
        """, (application_id, ))

        answers_dict = {row['question_id']: row for row in cursor.fetchall()}

        # Create DataFrame with original structure plus Answer column
        data = []
        for analysis in analyses:
            answer_data = answers_dict.get(analysis['id'])
            row = {
                'ID':
                analysis['id'],
                'Question':
                analysis['original_question'],
                'Category':
                analysis['category'],
                'Subcategory':
                analysis['subcategory'],
                'Tool':
                analysis['tool_suggestion'],
                'Answer':
                answer_data['answer']
                if answer_data else 'No answer collected',
                'Data Points':
                answer_data['data_points'] if answer_data else 0,
                'Risk Level':
                answer_data['risk_level'] if answer_data else 'Not assessed',
                'Compliance Status':
                answer_data['compliance_status']
                if answer_data else 'Not assessed'
            }
            data.append(row)

        df = pd.DataFrame(data)

        # Create Excel file in memory
        with tempfile.NamedTemporaryFile(delete=False,
                                         suffix='.xlsx') as tmp_file:
            with pd.ExcelWriter(tmp_file.name, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Audit Questions', index=False)

                # Get the workbook and worksheet to format
                workbook = writer.book
                worksheet = writer.sheets['Audit Questions']

                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[
                        column_letter].width = adjusted_width

            # Generate filename
            filename = f"{app_data['audit_name']}_Data_Collection_Results.xlsx"

            return send_file(
                tmp_file.name,
                as_attachment=True,
                download_name=filename,
                mimetype=
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals() and conn:
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
        cursor.execute(
            """
            UPDATE tool_connectors 
            SET connector_type = %s, configuration = %s, status = %s
            WHERE id = %s
            RETURNING id, application_id, ci_id, connector_type, configuration, status, created_at
        """, (data.get('connectorType'),
              json.dumps(data.get('configuration', {})),
              data.get('status', 'pending'), connector_id))

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
        cursor.execute("DELETE FROM tool_connectors WHERE id = %s",
                       (connector_id, ))

        if cursor.rowcount == 0:
            return jsonify({'error': 'Connector not found'}), 404

        conn.commit()

        return jsonify({
            'success': True,
            'message': 'Connector deleted successfully'
        }), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()


# This endpoint was moved below to avoid duplication


@app.route('/api/connectors/<int:connector_id>/test', methods=['POST'])
def test_connector_connection(connector_id):
    """Test connector connection and update status"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get connector configuration
        cursor.execute(
            """
            SELECT id, connector_type, configuration, ci_id
            FROM tool_connectors 
            WHERE id = %s
        """, (connector_id, ))

        connector = cursor.fetchone()
        if not connector:
            return jsonify({'error': 'Connector not found'}), 404

        connector_type = connector['connector_type']
        config = connector['configuration']

        # Test connection based on connector type
        test_result = test_connector_by_type(connector_type, config)

        # Update connector status based on test result
        new_status = 'active' if test_result['success'] else 'failed'
        cursor.execute(
            """
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
                cursor.execute(
                    "UPDATE tool_connectors SET status = 'failed' WHERE id = %s",
                    (connector_id, ))
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
            'message':
            'Missing required configuration: server and database are required',
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
                'message':
                f'Successfully connected to SQL Server {server}:{port}',
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
                'message':
                f'Cannot connect to SQL Server {server}:{port} - server unreachable',
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
            'message':
            'Missing required configuration: server and service_name are required',
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
                'message':
                f'Successfully connected to Oracle {server}:{port}/{service_name}',
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
                'message':
                f'Cannot connect to Oracle {server}:{port} - server unreachable',
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
        req = urllib.request.Request(
            test_url, headers={'User-Agent': 'CA-Audit-Agent/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()

            if status_code in [
                    200, 401, 403
            ]:  # 401/403 means server is reachable but needs auth
                return {
                    'success': True,
                    'message':
                    f'Successfully connected to Gnosis server {server}',
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
                    'message':
                    f'Gnosis server returned unexpected status: {status_code}',
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
        req = urllib.request.Request(
            test_url, headers={'User-Agent': 'CA-Audit-Agent/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()

            if status_code in [200, 401, 403]:
                return {
                    'success': True,
                    'message':
                    f'Successfully connected to Jira server {server}',
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
                    'message':
                    f'Jira server returned unexpected status: {status_code}',
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
        req = urllib.request.Request(
            test_url, headers={'User-Agent': 'CA-Audit-Agent/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()

            if status_code in [200, 401, 403]:
                return {
                    'success': True,
                    'message':
                    f'Successfully connected to QTest server {server}',
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
                    'message':
                    f'QTest server returned unexpected status: {status_code}',
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
        req = urllib.request.Request(
            test_url, headers={'User-Agent': 'CA-Audit-Agent/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()

            if status_code in [200, 401, 403]:
                return {
                    'success': True,
                    'message':
                    f'Successfully connected to ServiceNow instance {instance}',
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
                    'message':
                    f'ServiceNow instance returned unexpected status: {status_code}',
                    'duration': time.time() - start_time
                }
    except urllib.error.URLError as e:
        return {
            'success': False,
            'message':
            f'Cannot connect to ServiceNow instance {instance}: {str(e)}',
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


# Get connectors by CI ID endpoint (for Settings page)
@app.route('/api/connectors/ci/<string:ci_id>', methods=['GET'])
def get_connectors_by_ci(ci_id):
    """Get all connectors for a specific CI ID"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT id, application_id, ci_id, connector_name, connector_type, 
                   configuration, status, created_at
            FROM tool_connectors 
            WHERE ci_id = %s
            ORDER BY created_at DESC
        """, (ci_id, ))

        connectors = []
        for row in cursor.fetchall():
            connector_data = {
                'id':
                row['id'],
                'applicationId':
                row['application_id'],
                'ciId':
                row['ci_id'],
                'connectorName':
                row['connector_name'],
                'connectorType':
                row['connector_type'],
                'configuration':
                json.loads(row['configuration']) if isinstance(
                    row['configuration'], str) else
                (row['configuration'] if row['configuration'] else {}),
                'status':
                row['status'],
                'createdAt':
                row['created_at']
            }
            connectors.append(connector_data)

        return jsonify(connectors), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()


# ============= VERITAS GPT ENDPOINTS =============


@app.route('/api/context-documents/<string:ci_id>', methods=['GET'])
def get_context_documents(ci_id):
    """Get all context documents for a specific CI ID"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT id, ci_id, document_type, file_name, file_path, 
                   file_size, uploaded_at
            FROM context_documents 
            WHERE ci_id = %s
            ORDER BY uploaded_at DESC
        """, (ci_id, ))

        documents = []
        for row in cursor.fetchall():
            doc_data = {
                'id':
                row['id'],
                'ciId':
                row['ci_id'],
                'documentType':
                row['document_type'],
                'fileName':
                row['file_name'],
                'filePath':
                row['file_path'],
                'fileSize':
                row['file_size'],
                'uploadedAt':
                row['uploaded_at'].isoformat() if row['uploaded_at'] else None
            }
            documents.append(doc_data)

        return jsonify(documents), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()


@app.route('/api/context-documents/upload', methods=['POST'])
def upload_context_document():
    """Upload a context document for Veritas GPT"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        document_type = request.form.get('documentType')
        ci_id = request.form.get('ciId')

        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not document_type or not ci_id:
            return jsonify({'error':
                            'Document type and CI ID are required'}), 400

        if not allowed_document_file(file.filename):
            return jsonify({
                'error':
                'File type not allowed. Only PDF, DOC, DOCX, TXT files are supported'
            }), 400

        # Create audit folder structure: uploads/audit_<ci_id>/context_documents/
        context_folder = os.path.join(UPLOAD_FOLDER, f"audit_{ci_id}",
                                      "context_documents")
        os.makedirs(context_folder, exist_ok=True)

        # Save file with unique name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{document_type}_{timestamp}_{name}{ext}"
        file_path = os.path.join(context_folder, unique_filename)

        file.save(file_path)
        file_size = os.path.getsize(file_path)

        # Save to database
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            INSERT INTO context_documents 
            (ci_id, document_type, file_name, file_path, file_size, uploaded_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (ci_id, document_type, filename, file_path, file_size,
              datetime.now()))

        document_id = cursor.fetchone()['id']
        conn.commit()

        return jsonify({
            'message': 'Document uploaded successfully',
            'documentId': document_id,
            'fileName': filename,
            'fileSize': file_size
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()


@app.route('/api/context-documents/<int:document_id>', methods=['DELETE'])
def delete_context_document(document_id):
    """Delete a context document"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get document info first
        cursor.execute("SELECT file_path FROM context_documents WHERE id = %s",
                       (document_id, ))
        document = cursor.fetchone()

        if not document:
            return jsonify({'error': 'Document not found'}), 404

        # Delete file from filesystem
        try:
            if os.path.exists(document['file_path']):
                os.remove(document['file_path'])
        except OSError:
            pass  # Continue even if file deletion fails

        # Delete from database
        cursor.execute("DELETE FROM context_documents WHERE id = %s",
                       (document_id, ))
        conn.commit()

        return jsonify({'message': 'Document deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()


@app.route('/api/veritas-gpt/chat', methods=['POST'])
def veritas_gpt_chat():
    """Handle Veritas GPT chat requests with context-aware responses - gracefully handles missing documents"""
    conn = None
    cursor = None

    try:
        data = request.get_json()
        message = data.get('message')
        ci_id = data.get('ciId')
        audit_id = data.get('auditId')
        audit_name = data.get('auditName', 'Unknown Audit')

        if not message or not ci_id or not audit_id:
            return jsonify(
                {'error': 'Message, CI ID, and Audit ID are required'}), 400

        # Initialize context information
        context_docs = []
        data_requests = []
        execution_results = []
        context_info = []
        data_collection_info = []
        execution_info = []

        # Try to get database connection and fetch context, but don't fail if unavailable
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)

                # Try to get context documents for this CI
                try:
                    cursor.execute(
                        """
                        SELECT document_type, file_name, file_path, file_size
                        FROM context_documents 
                        WHERE ci_id = %s
                        ORDER BY uploaded_at DESC
                    """, (ci_id, ))
                    context_docs = cursor.fetchall() or []
                except Exception as db_error:
                    print(f"Context documents query failed: {db_error}")
                    context_docs = []

                # Try to get data collection forms for this audit
                try:
                    cursor.execute(
                        """
                        SELECT file_name, file_type, total_questions, categories, subcategories
                        FROM data_requests 
                        WHERE application_id = %s
                        ORDER BY uploaded_at DESC
                    """, (audit_id, ))
                    data_requests = cursor.fetchall() or []
                except Exception as db_error:
                    print(f"Data requests query failed: {db_error}")
                    data_requests = []

                # Try to get Step 4 execution results for this audit
                try:
                    cursor.execute(
                        """
                        SELECT question_id, result, status, execution_details
                        FROM agent_executions 
                        WHERE application_id = %s
                        ORDER BY question_id
                    """, (audit_id, ))
                    execution_results = cursor.fetchall() or []
                except Exception as db_error:
                    print(f"Agent executions query failed: {db_error}")
                    execution_results = []

        except Exception as conn_error:
            print(f"Database connection failed: {conn_error}")
            # Continue without database context

        # Build context information (gracefully handle missing data)
        try:
            for doc in context_docs:
                doc_type_label = {
                    'support_plan': 'Support Plan',
                    'design_diagram': 'Design Diagram',
                    'additional_supplements': 'Additional Supplements'
                }.get(doc.get('document_type', ''), 'Document')

                file_name = doc.get('file_name', 'Unknown File')
                file_size = doc.get('file_size', 0)
                context_info.append(
                    f"- {doc_type_label}: {file_name} ({file_size} bytes)")
        except Exception as e:
            print(f"Error building context info: {e}")

        # Build data collection forms information (gracefully handle missing data)
        try:
            for req in data_requests:
                file_type = req.get('file_type', 'unknown')
                file_type_label = "Primary Questions" if file_type == 'primary' else "Follow-up Questions"
                categories = req.get('categories', []) or []
                category_list = ", ".join(
                    categories) if categories else "Various"
                total_questions = req.get('total_questions', 0)
                file_name = req.get('file_name', 'Unknown File')
                data_collection_info.append(
                    f"- {file_type_label}: {file_name} ({total_questions} questions in {category_list})"
                )
        except Exception as e:
            print(f"Error building data collection info: {e}")

        # Build execution results information (Step 4 completed results)
        try:
            completed_count = 0
            total_count = len(execution_results)
            sample_findings = []

            for result in execution_results:
                if result.get('status') == 'completed':
                    completed_count += 1

                    # Extract findings from JSON result data
                    if len(sample_findings) < 3:
                        try:
                            result_data = json.loads(result.get(
                                'result', '{}')) if isinstance(
                                    result.get('result'), str) else result.get(
                                        'result', {})
                            question_id = result.get('question_id', 'Unknown')

                            # Get findings from the result JSON
                            findings_list = result_data.get('findings', [])
                            if findings_list:
                                finding_text = findings_list[0].get(
                                    'finding', 'No findings available'
                                )[:80] + '...' if len(findings_list[0].get(
                                    'finding',
                                    '')) > 80 else findings_list[0].get(
                                        'finding', '')
                                sample_findings.append(
                                    f"  • {question_id}: {finding_text}")
                            else:
                                # Try executive summary
                                exec_summary = result_data.get(
                                    'analysis',
                                    {}).get('executiveSummary', '')
                                if exec_summary:
                                    summary_text = exec_summary[:80] + '...' if len(
                                        exec_summary) > 80 else exec_summary
                                    sample_findings.append(
                                        f"  • {question_id}: {summary_text}")
                        except (json.JSONDecodeError,
                                AttributeError) as parse_error:
                            print(f"Error parsing result JSON: {parse_error}")

            if total_count > 0:
                execution_info.append(
                    f"- Execution Status: {completed_count}/{total_count} questions completed"
                )
                if sample_findings:
                    execution_info.append("- Sample Findings:")
                    execution_info.extend(sample_findings)
        except Exception as e:
            print(f"Error building execution info: {e}")

        # Create context-aware system prompt with graceful degradation
        context_section = chr(10).join(
            context_info
        ) if context_info else "No context documents are currently available for this CI."
        data_collection_section = chr(10).join(
            data_collection_info
        ) if data_collection_info else "No data collection forms are currently available for this audit."
        execution_section = chr(10).join(
            execution_info
        ) if execution_info else "No execution results are currently available for this audit."

        system_prompt = f"""You are Veritas GPT, an AI assistant specialized in audit data collection and analysis for audit "{audit_name}" (CI {ci_id}).

CONTEXT DOCUMENTS AVAILABLE FOR THIS CI:
{context_section}

DATA COLLECTION FORMS FOR THIS AUDIT (Step 2):
{data_collection_section}

EXECUTION RESULTS FOR THIS AUDIT (Step 4):
{execution_section}

Your role is to:
1. Provide accurate, helpful responses about audit processes and data collection
2. Reference available context documents, data collection forms, AND execution results when relevant
3. Help users understand audit questions, requirements, workflows, and completed findings
4. Analyze completed execution results to provide insights and recommendations
5. Maintain a professional, helpful tone focused on audit excellence

You have access to:
- Context documents uploaded for the CI system
- Data collection forms with audit questions and categories (Step 2)
- Completed execution results with findings and answers (Step 4)
- General audit best practices and methodologies

When answering questions, leverage all available context including:
- Specific audit questions from data collection forms
- Completed findings and results from execution
- Context about the CI system being audited
- Industry-standard audit approaches and recommendations

Please provide detailed, actionable responses while referencing the specific context available for this audit."""

        # Use Langchain to generate response (ensure we're using Langchain not direct OpenAI)
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=message)
            ]

            # Ensure we're using the Langchain llm object, not direct OpenAI
            response = llm.invoke(messages)
            response_content = response.content

        except Exception as llm_error:
            print(f"LLM invocation error: {llm_error}")
            # Provide graceful fallback response
            response_content = f"""I apologize, but I'm currently experiencing technical difficulties with the AI response system. 

However, I can still help you with your audit question about "{audit_name}" (CI {ci_id}).

Based on your query: "{message}"

Here are some general audit guidance points:
- Ensure all audit documentation is properly organized and accessible
- Follow systematic data collection procedures for consistency
- Validate data sources and maintain audit trails
- Document findings clearly with supporting evidence

Please try your question again, or contact your system administrator if the issue persists."""

        return jsonify({
            'response': response_content,
            'contextDocuments': len(context_docs),
            'dataCollectionForms': len(data_requests),
            'executionResults': len(execution_results),
            'auditName': audit_name,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }), 200

    except Exception as e:
        print(f"Veritas GPT error: {str(e)}")
        # Provide user-friendly error with graceful degradation
        error_response = f"""I encountered an issue while processing your request, but I can still provide general audit guidance.

For audit "{audit_name}" (CI {ci_id}), regarding your question: "{message or 'your audit inquiry'}"

General recommendations:
- Review available audit documentation and context materials
- Follow established audit procedures and protocols  
- Ensure proper data collection and validation processes
- Document all findings with appropriate detail

Please try again or contact support if issues persist."""

        return jsonify({
            'response': error_response,
            'contextDocuments': 0,
            'dataCollectionForms': 0,
            'executionResults': 0,
            'auditName': audit_name,
            'timestamp': datetime.now().isoformat(),
            'status': 'error_handled'
        }), 200

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == '__main__':
    print("🐍 Starting Simple Flask API server...")
    print("📡 CORS enabled for React frontend at http://localhost:5000")
    print("🔗 Flask backend running at http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)
