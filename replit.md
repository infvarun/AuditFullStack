# replit.md

## Overview

This is a full-stack audit data collection application designed to streamline and automate audit processes. It features a wizard-based interface for setting up audit data collection, managing tool connectors, and generating audit reports. The application aims to provide a comprehensive solution for managing complex audit workflows, from initial setup to final report generation, leveraging AI for intelligent question analysis and agent execution for data collection.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend
- **Framework**: React 18 with TypeScript
- **Routing**: Wouter
- **State Management**: TanStack Query (React Query)
- **UI Framework**: shadcn/ui built on Radix UI
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **Form Management**: React Hook Form with Zod validation

### Backend
- **Framework**: Python Flask with Flask-CORS
- **Database**: PostgreSQL with psycopg2
- **Database Provider**: Neon Database (serverless PostgreSQL)
- **API**: RESTful JSON API
- **AI Integration**: LangChain with OpenAI (GPT-4o) for intelligent question analysis and agent execution.

### Core Features
- **Wizard Flow**: Guides users through application setup, data request, tool connector configuration, data collection, and results viewing.
- **Application Setup**: Defines basic application information and settings.
- **Data Request**: Handles file uploads (e.g., Excel) and question parsing. Supports dual file upload for primary and follow-up questions.
- **Tool Connectors**: Configures external system integrations (SQL Server, Oracle, Gnosis, Jira, QTest, ServiceNow, NAS). Connectors are CI-based.
- **AI-Powered Question Analysis**: Utilizes OpenAI GPT-4o via LangChain to analyze audit questions, suggest tools, and assign connectors.
- **Agent Execution**: Real AI agent execution with progress tracking, result persistence, and status preservation across navigation.
- **Excel Export**: Generates populated data collection sheets with audit answers and findings.
- **Audit Status Management**: Complete workflow with "Finish Audit" functionality and bidirectional status control (Complete ↔ In Progress).
- **Data Persistence**: Full persistence of execution results with proper state management across all wizard steps.
- **Audit Deletion**: Comprehensive deletion functionality for entire audits and associated data.

### Data Flow
1. Application Creation: User defines audit metadata with status tracking.
2. File Processing: Data request files are uploaded and parsed for questions.
3. AI Analysis: Questions are analyzed to suggest tools and connectors.
4. Connector Configuration: External systems are configured.
5. Data Collection: AI agents execute data gathering with real results and persistence.
6. Result Generation: Audit results are compiled, exported to Excel, and status managed.
7. Audit Completion: Status management with confirmation dialogs and bidirectional control.

### Deployment Strategy
- **Development**: React frontend on port 5000 (Vite), Python Flask backend on port 8000. Direct CORS communication.
- **Production**: Static React files served, Python Flask backend for API and data processing.

## External Dependencies

### Frontend Dependencies
- **UI Components**: Radix UI
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query
- **Form Handling**: React Hook Form, Zod
- **Animations**: Framer Motion, Lottie (previously, now GIF)
- **Date Handling**: date-fns

### Backend Dependencies
- **Database**: PostgreSQL (via psycopg2) with status field for audit state management
- **AI Processing**: LangChain, OpenAI (GPT-4o) for real agent execution
- **Excel Handling**: openpyxl for populated data collection sheet generation
- **Web Server**: Flask with comprehensive audit lifecycle API endpoints
- **File Storage**: Physical audit folders with organized file management

## Recent Achievements (August 2025)
- ✅ **Full Audit Lifecycle**: Complete 5-step wizard with real data integration
- ✅ **AI Agent Execution**: 28-question execution with authentic audit findings
- ✅ **Data Persistence**: Step 4 execution results persist across navigation
- ✅ **Excel Export**: Populated data collection sheets with audit answers
- ✅ **Status Management**: Bidirectional audit completion with confirmation dialogs
- ✅ **Real Data Integration**: No mock data - all results from authentic AI analysis
- ✅ **Veritas GPT Enhancement**: Multi-audit support with context-aware chat interface including improved input design
- ✅ **Local Setup Guide**: Comprehensive LOCAL_SETUP.md with pip dependencies for local development
- ✅ **File-Based Data Connectors**: Migrated from mock data to realistic file-based system using server/tools folder structure with CI-organized tool-specific data files (Excel, documents) for authentic audit data collection
- ✅ **Enhanced Sample Questions**: Generated comprehensive audit question sheets (14 primary + 7 follow-up) with multi-tool integration targeting realistic data scenarios (16 multi-tool questions covering Access Controls, Change Management, Documentation, Quality Assurance)
- ✅ **Clean Data Collection Display**: Fixed Step 4 JSON parsing issues with simple extraction of Executive Summary content from LLM responses, removing markdown formatting and displaying clean readable text (August 6, 2025)
- ✅ **Save Persistence Fix**: Resolved critical database schema mismatch where Step 5 API was querying non-existent columns (confidence, risk_level, etc.) in agent_executions table. Fixed backend to use correct column names and properly retrieve execution results for Step 5 display (August 6, 2025)
- ✅ **Step 5 Modal Data Fix**: Fixed JSON parsing in Step 5 modal to correctly extract confidence values from analysis.confidence and tool information from toolsUsed array in agent_executions.result column. Modal now displays actual confidence scores and tool names instead of "N/A" and "Unknown" (August 6, 2025)
- ✅ **Enhanced Excel Export**: Replaced multiple download options with single "Execution Results & Analysis" Excel export containing Step 5 table data including question ID, original question, executive summary, risk level, compliance status, data points, confidence, tool used, and findings summary (August 6, 2025)
- ✅ **Veritas GPT LangChain Integration**: Fixed Veritas GPT to use existing configured LangChain OpenAI setup instead of requiring separate API key. Agent now uses shared Flask application LLM instance for seamless integration with established authentication and configuration (August 6, 2025)
- ✅ **Authentic Tool Data Analysis**: Enhanced Veritas GPT to successfully read and analyze actual CI tool data files (Excel/text) from folder structure. Agent now provides data-driven responses using authentic SQL Server user roles, Oracle database info, and other tool-specific data instead of generic responses (August 6, 2025)