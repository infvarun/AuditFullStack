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