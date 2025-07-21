# replit.md

## Overview

This is a full-stack audit data collection application built with React + TypeScript frontend and Express.js backend. The application provides a wizard-based interface for setting up audit data collection processes, managing tool connectors, and generating audit reports. It uses a PostgreSQL database with Drizzle ORM for data management and includes a comprehensive UI component system built with shadcn/ui.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: React 18 with TypeScript
- **Routing**: Wouter for client-side routing
- **State Management**: TanStack Query (React Query) for server state management
- **UI Framework**: shadcn/ui components built on Radix UI primitives
- **Styling**: Tailwind CSS with custom CSS variables for theming
- **Build Tool**: Vite for development and production builds
- **Form Management**: React Hook Form with Zod validation

### Backend Architecture
- **Framework**: Python Flask with Flask-CORS for clean API development
- **Database**: PostgreSQL with psycopg2 direct connection
- **Database Provider**: Neon Database (serverless PostgreSQL)
- **API**: RESTful JSON API with comprehensive Excel processing
- **Development**: Flask development server with debug mode and hot reload
- **CORS**: Flask-CORS middleware for seamless React frontend communication

## Key Components

### Database Schema
- **Applications**: Core application records with CI IDs and date ranges
- **Data Requests**: File uploads and question parsing results
- **Tool Connectors**: External system integrations (SQL Server, Outlook, etc.)
- **Data Collection Sessions**: Progress tracking for data gathering
- **Audit Results**: Final audit outcomes and document generation

### Wizard Flow
1. **Application Setup**: Basic application information and settings
2. **Data Request**: File upload and question parsing
3. **Tool Connectors**: Configure external system connections
4. **Data Collection**: Execute data gathering with progress tracking
5. **Results**: View audit results and download reports

### External Integrations
- SQL Server database connections
- Outlook Exchange email systems
- ServiceNow (SNow) integration
- NAS file systems
- Gnosis knowledge management
- ADC (Application Dependency Checking)

## Data Flow

1. **Application Creation**: User creates application with basic metadata
2. **File Processing**: Data request files are uploaded and parsed for questions
3. **Connector Configuration**: External systems are configured with credentials
4. **Data Collection**: Automated data gathering from configured sources
5. **Result Generation**: Audit results are compiled and made available for download

## External Dependencies

### Frontend Dependencies
- **UI Components**: Extensive Radix UI component library
- **Styling**: Tailwind CSS with PostCSS processing
- **State Management**: TanStack Query for API state
- **Form Handling**: React Hook Form with Zod validation
- **Animations**: Framer Motion for UI animations
- **Date Handling**: date-fns for date manipulation

### Backend Dependencies
- **Database**: SQLAlchemy ORM with PostgreSQL dialect
- **AI Processing**: LangChain with OpenAI integration
- **API Framework**: FastAPI with Pydantic models
- **Database Connection**: asyncpg for PostgreSQL connections
- **File Processing**: openpyxl for Excel file handling

## Deployment Strategy

### Development
- **Frontend**: Vite dev server with HMR on port 5000
- **Backend**: Python Flask with debug mode and hot reload on port 8000
- **Database**: Neon PostgreSQL with direct psycopg2 connections
- **Build**: Vite for frontend, Python Flask for backend execution
- **Communication**: Direct API calls with Flask-CORS configuration

### Production
- **Frontend**: Static files built with Vite
- **Backend**: Python Flask for production deployment
- **Database**: Direct PostgreSQL connection via psycopg2
- **Environment**: DATABASE_URL required for database connectivity

### Build Process
- Frontend assets built via Vite to `dist/public`
- Python Flask backend runs directly via `server/app.py`
- Database schema managed through direct SQL operations
- Clean separation with no proxy layer required

The application follows a pure separation architecture with React frontend and Python Flask backend communicating directly via Flask-CORS enabled API calls. The frontend uses TypeScript for type safety while the backend uses native Python types and JSON serialization, maintaining complete separation between frontend and backend concerns.

## Recent Changes: Latest modifications with dates

### July 16, 2025 - Node.js Excel Processing & Follow-up Questions Integration
- **✓ Migrated from Python Flask to Node.js Excel processing** using xlsx library for better integration
- **✓ Fixed XLSX library import and usage** for proper ES module compatibility
- **✓ Added comprehensive Excel column mapping** with Question Number, Process, Sub-Process, and Question fields
- **✓ Implemented dual file upload system** - Primary Data Request Files and Follow-up Question Files
- **✓ Updated database schema** with fileType, categories, subcategories, and columnMappings JSON fields
- **✓ Enhanced Step 2 UI** with dynamic column selection, sample data preview, and validation
- **✓ Added real-time file processing** with buffer-based Excel parsing
- **✓ Removed estimated time display** as requested
- **✓ Created comprehensive error handling** and progress tracking for file uploads
- **✓ Added conditional follow-up files support** - only shows when "Enable follow-up questions" is checked in Step 1
- **✓ Integrated Node.js API endpoints** for column detection and file processing
- **✓ Updated database storage** to handle complex JSON structures for questions and categories

### July 16, 2025 - Dashboard and Navigation System
- **Added comprehensive dashboard landing page** with search functionality for existing applications
- **Implemented navigation between dashboard and wizard** with URL-based routing
- **Added "Recent Audits" section** with card-based display of recent applications
- **Created unified navigation header** with back button, logo, settings, and user avatar
- **Added application search feature** with real-time filtering by name or CI ID
- **Implemented "Initiate new audit" button** for starting fresh audit processes
- **Added URL parameter support** for editing existing applications (`/wizard/:applicationId`)
- **Enhanced wizard with context awareness** - shows existing application name in header
- **Added API routes for fetching all applications** and individual application details
- **Removed form validation from all wizard steps** to allow free navigation for testing

### July 16, 2025 - CI-Based Connector Configuration & Settings System
- **✓ Redesigned Step 3 to blank placeholder** directing users to Settings page for connector configuration
- **✓ Created comprehensive Settings page** with CI search, connector management, and configuration interface
- **✓ Updated database schema** to support CI-based connector configurations with unique constraints
- **✓ Added ciId field to tool connectors** linking connectors to applications by CI ID
- **✓ Implemented 4 core connector types** - SQL Server, Gnosis Path, ServiceNow, and NAS Path
- **✓ Added Settings navigation button** in wizard header for easy access to connector management
- **✓ Created CI-based connector API routes** for create, read, update, and delete operations
- **✓ Enhanced storage interface** with CI-specific connector querying and management methods
- **✓ Updated routing system** to include Settings page at `/settings` path
- **✓ Applied database migration** to reflect new schema with ciId and unique constraint support

### July 16, 2025 - AI-Powered Question Analysis System
- **✓ Redesigned Step 3 with AI-powered question analysis** replacing static connector configuration
- **✓ Moved connector configuration to dashboard** with "Add Connector" button beside "Create First Audit"
- **✓ Integrated OpenAI GPT-4o for intelligent question analysis** with efficient prompt generation
- **✓ Created comprehensive data table** with 4 columns: original question, AI prompt, tool suggestion, connector
- **✓ Added editable tool suggestions** allowing users to modify AI recommendations
- **✓ Implemented expandable row details** for full prompt viewing and question categorization
- **✓ Added real-time question analysis** with loading states and error handling
- **✓ Created backend API endpoint** `/api/questions/analyze` for AI-powered question processing
- **✓ Enhanced UI with badges and visual indicators** for analysis status and tool assignments
- **✓ Added re-analysis functionality** for iterative question optimization

### July 17, 2025 - Enhanced Progress Tracking & Persistence
- **✓ Added live progress bar** showing real-time completion percentage during AI analysis
- **✓ Integrated Lottie animation** for engaging loading states with Assistant Bot animation
- **✓ Created question analysis database table** for persistent storage of AI-generated results
- **✓ Added save/load functionality** to prevent re-analysis on page refreshes
- **✓ Implemented progress calculation** showing X of Y questions complete with percentage
- **✓ Added save button with visual feedback** and green checkmark when analyses are saved
- **✓ Enhanced storage interface** with question analysis CRUD operations
- **✓ Updated database schema** with questionAnalyses table and unique constraints
- **✓ Added API endpoints** for saving, loading, and managing question analyses
- **✓ Applied database migration** to support new question analysis persistence
- **✓ Enabled persistent Save button** allowing users to save tool suggestion changes at any time
- **✓ Added state reset functionality** to mark changes as unsaved when users modify tool suggestions
- **✓ Replaced Lottie animation with animated GIF** using user-provided Assistant Bot GIF file
- **✓ Moved GIF to public/assets folder** for proper web accessibility

### July 17, 2025 - Complete Migration to Python Backend
- **✓ Successfully migrated from Node.js Express to Python FastAPI** with complete backend replacement
- **✓ Removed all Node.js server files** (index.ts, routes.ts, storage.ts, db.ts, vite.ts)
- **✓ Created comprehensive Python FastAPI server** with main.py handling all API endpoints
- **✓ Integrated LangChain with GPT-4o model** for intelligent question analysis and prompt generation
- **✓ Added async SQLAlchemy ORM** with PostgreSQL and asyncpg driver for database operations
- **✓ Implemented FastAPI with async/await patterns** for high-performance API endpoints
- **✓ Added CORS middleware and request logging** for proper frontend-backend communication
- **✓ Created QuestionAnalysisService class** using LangChain for structured AI prompt generation
- **✓ Added comprehensive error handling** with fallback responses for AI analysis failures
- **✓ Implemented batch question analysis** for processing multiple questions efficiently
- **✓ Added health check endpoint** for monitoring Python server status
- **✓ Created database models** for applications, data requests, question analyses, and data collection sessions
- **✓ Configured proper Python server startup** with uvicorn and hot reload support
- **✓ Added environment variable support** for OpenAI API key and database configuration
- **✓ Built React frontend** to work with Python backend API endpoints
- **✓ Configured static file serving** for React app from Python FastAPI server
- **✓ Updated architecture to React + Python** - completely eliminated Node.js server dependency

### July 17, 2025 - Fixed Application Startup & Architecture Optimization
- **✓ Resolved missing server/index.ts file** that was causing application startup failures
- **✓ Created Node.js proxy server** to serve React frontend and route API calls to Python backend
- **✓ Fixed port conflicts** by running Python backend on port 8000 and Node.js proxy on port 5000
- **✓ Installed http-proxy-middleware** for proper API request routing between frontend and backend
- **✓ Updated replit.md architecture documentation** to reflect hybrid React + Python setup
- **✓ Configured proper process management** with graceful shutdown handling for both servers
- **✓ Restored application functionality** with working React frontend and Python FastAPI backend
- **✓ Maintained separation of concerns** - React handles UI, Python handles AI processing and data storage

### July 17, 2025 - Complete API Communication Fix & Documentation
- **✓ Fixed critical JSON body parsing issue** in Node.js proxy server for POST requests
- **✓ Replaced fetch with Node.js HTTP module** to eliminate content-length header mismatches
- **✓ Resolved database schema inconsistency** by adding missing created_at column to data_collection_sessions
- **✓ Verified all API endpoints working correctly** - /api/applications, /api/data-collection/start, /api/excel/get-columns
- **✓ Confirmed React frontend and Python backend communication** through proxy server
- **✓ Created comprehensive README.md documentation** with complete setup guide, architecture explanation, and development guidelines
- **✓ Added detailed wizard step customization guide** for future development and modifications
- **✓ Documented complete data flow and API endpoint specifications** for maintainability

### July 18, 2025 - Eliminated Node.js Proxy Architecture
- **✓ Removed Node.js proxy server** (server/index.ts) completely from the architecture
- **✓ Configured direct CORS communication** between React frontend and Python backend
- **✓ Updated Python FastAPI with proper CORS middleware** for localhost:5173 and other development ports
- **✓ Modified React frontend API client** to connect directly to Python backend on port 5000
- **✓ Created separate server startup scripts** for independent development workflow
- **✓ Updated package.json dev script** to run only Vite dev server for React frontend
- **✓ Added environment configuration** with VITE_API_URL for backend endpoint specification
- **✓ Created comprehensive database DDL and DML scripts** with sample data and realistic audit scenarios
- **✓ Updated architecture documentation** to reflect direct frontend-backend communication
- **✓ Verified API endpoints working** with direct backend communication (no proxy layer)

### July 18, 2025 - Fixed Application Startup and Replit Host Configuration
- **✓ Resolved server/index.ts missing file error** that was preventing application startup
- **✓ Created unified server startup process** launching both React frontend and Python backend
- **✓ Configured React frontend on port 5000** using Vite dev server with proper host configuration
- **✓ Set up Python FastAPI backend on port 8000** with correct port allocation
- **✓ Fixed Replit host domain blocking issue** by configuring Vite with proper environment variables
- **✓ Verified database connectivity and initialization** ensuring proper PostgreSQL connection
- **✓ Implemented proper process management** with graceful shutdown handling for both servers
- **✓ Confirmed application accessibility** on Replit platform with working frontend and backend communication

### July 21, 2025 - Clean Architecture Migration to React + Flask
- **✓ Eliminated Express.js complexity** replacing hybrid Node.js/Python setup with clean separation
- **✓ Created pure Python Flask backend** with Flask-CORS for seamless React communication
- **✓ Simplified server architecture** removing unnecessary Node.js proxy layer
- **✓ Updated React frontend API client** to communicate directly with Flask backend on port 8000
- **✓ Configured independent server scripts** for React (port 5000) and Flask (port 8000) development
- **✓ Added concurrently support** for running both servers simultaneously during development
- **✓ Created comprehensive Flask API** with applications, Excel processing, and health check endpoints
- **✓ Implemented direct PostgreSQL connections** using psycopg2 for better performance
- **✓ Updated architecture documentation** to reflect clean React + Flask separation
- **✓ Verified successful deployment** with both servers running independently and communicating properly
- **✓ Fixed database schema property mapping** between Flask API and React frontend (auditName, auditDateFrom, etc.)
- **✓ Configured CORS for Replit hosting environment** with proper domain and credential support
- **✓ Updated API URL configuration** to use 0.0.0.0:8000 for proper network access
- **✓ Cleaned up all unused files** removing old Python servers, shell scripts, logs, and sample data files