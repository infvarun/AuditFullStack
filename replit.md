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
- **Agent Execution**: Simulates data collection based on configured tools, with progress tracking and result display.
- **Audit Deletion**: Comprehensive deletion functionality for entire audits and associated data.

### Data Flow
1. Application Creation: User defines audit metadata.
2. File Processing: Data request files are uploaded and parsed for questions.
3. AI Analysis: Questions are analyzed to suggest tools and connectors.
4. Connector Configuration: External systems are configured.
5. Data Collection: Automated data gathering from configured sources.
6. Result Generation: Audit results are compiled and reported.

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
- **Database**: PostgreSQL (via psycopg2)
- **AI Processing**: LangChain, OpenAI (GPT-4o)
- **Excel Handling**: openpyxl
- **Web Server**: Flask
- **Database ORM**: SQLAlchemy (for conceptual understanding, but psycopg2 is direct)