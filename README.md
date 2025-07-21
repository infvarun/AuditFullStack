# CA Audit Agent - AI-Powered Audit Data Collection Platform

A sophisticated audit data collection application that intelligently matches audit questions with appropriate data connectors and collection strategies. Built with React + TypeScript frontend, Python Flask backend, and powered by OpenAI GPT-4o for intelligent question analysis.

## 🚀 Quick Start

### Prerequisites
- **Node.js 20+** for React frontend
- **Python 3.11+** for Flask backend  
- **PostgreSQL database** (provided by Replit)
- **OpenAI API Key** for AI question analysis

### 1. Environment Setup

Create a `.env.local` file in the root directory:

```bash
# Required: OpenAI API Key for AI question analysis
OPENAI_API_KEY=sk-your-openai-api-key-here

# Required: Backend API URL for frontend communication
VITE_API_URL=http://localhost:8000

# Auto-provided by Replit: PostgreSQL Database Connection
DATABASE_URL=postgresql://username:password@host:port/database
```

### 2. Get Your OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to **API Keys** section
4. Click **"Create new secret key"**
5. Copy the key (starts with `sk-`) and add it to your `.env.local`

**Important**: Keep your API key secure and never commit it to version control.

### 3. Start the Application

```bash
# Install dependencies and start both servers
npm run dev
```

This command starts:
- **React frontend** on `http://localhost:5000`
- **Flask backend** on `http://localhost:8000`

### 4. Verify Setup

1. Open `http://localhost:5000` in your browser
2. You should see the CA Audit Agent dashboard
3. Create a test audit to verify OpenAI integration works

## 🏗️ Architecture Overview

### Technology Stack
- **Frontend**: React 18 + TypeScript + Vite
- **Backend**: Python Flask + Flask-CORS
- **Database**: PostgreSQL with psycopg2
- **AI**: OpenAI GPT-4o via Langchain
- **UI**: shadcn/ui components + Tailwind CSS
- **File Processing**: xlsx library for Excel parsing

### Core Features
- **Dashboard**: Search and manage existing audit applications
- **4-Step Wizard**: Complete audit setup workflow
- **Excel Processing**: Upload and parse data request files
- **AI Question Analysis**: Intelligent tool recommendations
- **6 Connector Types**: SQL Server, Oracle, Gnosis, Jira, QTest, ServiceNow
- **Agent Execution**: Automated data collection simulation
- **Progress Tracking**: Real-time updates and status monitoring

## 📁 Project Structure

```
├── .env.local              # Environment variables (create this)
├── client/                 # React frontend application
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   │   ├── ui/         # shadcn/ui component library
│   │   │   └── wizard/     # Wizard step components
│   │   ├── pages/          # Main application pages
│   │   │   ├── dashboard.tsx
│   │   │   └── wizard.tsx
│   │   ├── lib/            # Utilities and API client
│   │   └── hooks/          # Custom React hooks
├── server/                 # Python Flask backend
│   ├── simple_flask.py     # Main Flask application
│   └── uploads/            # File upload storage
├── shared/                 # Shared TypeScript schemas
│   └── schema.ts           # Database schema definitions
├── public/                 # Static assets
└── package.json            # Node.js dependencies
```

## 🔗 API Endpoints

### Application Management
- `GET /api/applications` - List all audit applications
- `POST /api/applications` - Create new audit application
- `GET /api/applications/:id` - Get specific application details
- `PUT /api/applications/:id` - Update application
- `DELETE /api/applications/:id` - Delete application and all data

### File Processing
- `POST /api/excel/get-columns` - Analyze Excel file structure
- `POST /api/data-requests` - Save processed file data

### AI Analysis
- `POST /api/questions/analyze` - Analyze questions with AI
- `GET /api/questions/analyze/:appId` - Get saved analyses
- `POST /api/questions/save` - Save analysis results

### Agent Execution
- `POST /api/agent/execute` - Start agent execution
- `GET /api/agent/executions/:appId` - Get execution results

## 🗃️ Database Schema

### Core Tables

**applications**
- `id` - Primary key
- `name` - Application identifier  
- `audit_name` - Human-readable audit name
- `ci_id` - Configuration Item ID
- `start_date` / `end_date` - Audit date range
- `enable_followup_questions` - Boolean flag
- `created_at` - Timestamp

**data_requests**
- `id` - Primary key
- `application_id` - Foreign key to applications
- `file_name` - Original Excel filename
- `file_type` - Primary or followup file type
- `questions` - JSON array of parsed questions
- `total_questions` - Question count
- `column_mappings` - JSON mapping configuration

**question_analyses**
- `id` - Primary key
- `application_id` - Foreign key to applications
- `question_id` - Unique question identifier
- `original_question` - Source question text
- `ai_prompt` - Generated AI prompt
- `suggested_tool` - Recommended connector tool
- `analysis_result` - Complete AI response

**agent_executions**
- `id` - Primary key
- `application_id` - Foreign key to applications
- `question_id` - Associated question
- `tool_type` - Selected connector tool
- `prompt` - Execution prompt
- `result` - Execution result
- `status` - Success/failure status

## 🛠️ Local Development

### Development Commands

```bash
# Start development servers
npm run dev

# Type checking
npm run check

# Build for production
npm run build

# Start production server
npm start
```

### Development Workflow

1. **Frontend Development**: Edit files in `client/src/`
   - React components auto-reload via Vite HMR
   - TypeScript compilation happens automatically
   - Tailwind CSS changes reflect immediately

2. **Backend Development**: Edit `server/simple_flask.py`
   - Flask debug mode enables auto-reload
   - Python changes restart the server automatically
   - Database changes require manual testing

3. **Database Changes**: Use SQL tool or direct PostgreSQL access
   - Schema changes should be documented
   - Test data can be added via SQL commands

### Debugging Tips

1. **Check Server Logs**: Both React and Flask logs appear in terminal
2. **API Testing**: Use browser dev tools or curl for API requests
3. **Database Issues**: Verify DATABASE_URL in environment
4. **OpenAI Errors**: Check API key and account credits
5. **CORS Issues**: Ensure both servers are running on correct ports

## 🚀 Deployment (Replit)

### Environment Variables in Replit

1. Go to your Replit project
2. Click on "Secrets" (lock icon) in left sidebar
3. Add these secrets:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `DATABASE_URL`: Auto-provided by Replit

### Replit Configuration

The app is pre-configured for Replit with:
- **CORS**: Automatic handling for `.replit.app` domains
- **Network Binding**: `0.0.0.0` for proper external access
- **Process Management**: Graceful shutdown handling
- **File Storage**: `uploads/` directory for audit files

## 🔧 Troubleshooting

### Common Issues

**1. OpenAI API Errors**
```
Error: OpenAI API key not found
```
- Verify `OPENAI_API_KEY` in `.env.local`
- Check OpenAI account has credits
- Ensure key starts with `sk-`

**2. Database Connection Issues**
```
Error: Database connection failed
```
- Check `DATABASE_URL` environment variable
- Verify PostgreSQL is running
- Test connection manually

**3. CORS Errors**
```
Access blocked by CORS policy
```
- Ensure Flask server is running on port 8000
- Check `VITE_API_URL` points to correct backend
- Verify both servers started successfully

**4. File Upload Issues**
```
Excel processing failed
```
- Check file format is .xlsx or .xls
- Verify file has proper column structure
- Ensure uploads/ directory exists

### Getting Help

1. Check the console logs in your browser developer tools
2. Review server terminal output for error messages
3. Verify all environment variables are properly set
4. Test API endpoints individually using curl or Postman

## 📝 Recent Updates

- **July 21, 2025**: Added complete audit deletion functionality with file cleanup
- **July 21, 2025**: Fixed server startup and CORS configuration issues  
- **July 21, 2025**: Migrated to Langchain for better AI integration
- **July 21, 2025**: Implemented agent execution system with progress tracking
- **July 21, 2025**: Added 6 connector types with intelligent tool selection
- **July 18, 2025**: Eliminated Node.js proxy, direct React + Flask communication
- **July 17, 2025**: Complete migration from Node.js Express to Python Flask backend