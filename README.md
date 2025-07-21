# Audit Data Collection Application

A sophisticated React + Flask audit data collection platform that provides intelligent workflow management and seamless user experience for complex audit configuration processes.

## Architecture

### Clean Separation Design
- **Frontend**: React 18 with TypeScript, Vite build system
- **Backend**: Python Flask with Flask-CORS for API communication
- **Database**: PostgreSQL with direct psycopg2 connections
- **UI Components**: shadcn/ui components built on Radix UI primitives
- **Styling**: Tailwind CSS with custom theming

### Key Features
- **Dashboard**: Search and manage existing audit applications
- **Wizard Interface**: Multi-step audit setup process
- **File Processing**: Excel file upload and column mapping
- **AI Integration**: Question analysis and tool suggestions
- **Real-time Progress**: Live updates during data processing

## Development

### Prerequisites
- Node.js 20+ for React frontend
- Python 3.11+ for Flask backend
- PostgreSQL database

### Quick Start
```bash
# Start both servers
npm run dev
```

This will start:
- React frontend on port 5000
- Flask backend on port 8000

### Project Structure
```
├── client/              # React frontend
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── pages/       # Application pages
│   │   └── lib/         # Utilities and API client
├── server/              # Flask backend
│   ├── simple_flask.py  # Main Flask application
│   └── uploads/         # File upload storage
├── shared/              # Shared TypeScript types
└── public/              # Static assets
```

### API Endpoints
- `GET /api/applications` - List all audit applications
- `POST /api/applications` - Create new audit application
- `GET /api/applications/:id` - Get specific application
- `POST /api/excel/get-columns` - Process Excel file uploads
- `GET /health` - Health check endpoint

## Database Schema

### Applications Table
- Primary audit application records
- Includes audit name, CI ID, date ranges
- Created timestamp tracking

### Data Requests Table
- File upload tracking
- Excel column mapping storage
- Question parsing results

### Tool Connectors Table
- External system integration configurations
- CI-based connector management

### Question Analyses Table
- AI-powered question analysis results
- Tool suggestion storage
- Prompt generation tracking

## Environment Configuration

Required environment variables:
```bash
DATABASE_URL=postgresql://...
VITE_API_URL=http://0.0.0.0:8000
```

## Deployment

The application is designed for Replit deployment with:
- Automatic CORS configuration for Replit domains
- Network binding to 0.0.0.0 for proper access
- Independent server processes with graceful shutdown

## Recent Updates

- Migrated from Node.js/Express to clean React + Flask architecture
- Fixed database schema property mapping issues
- Configured CORS for Replit hosting environment
- Cleaned up unused files and streamlined project structure
- Updated API communication for direct frontend-backend connection