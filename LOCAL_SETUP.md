# Local Development Setup Guide

This guide helps you set up the audit application on your local machine.

## Python Dependencies

Run the following pip install commands to install all required Python packages:

### Core Flask Dependencies
```bash
pip install Flask==3.0.3
pip install Flask-CORS==4.0.1
pip install Werkzeug==3.0.3
```

### Database
```bash
pip install psycopg2-binary==2.9.9
```

### Excel/Data Processing
```bash
pip install pandas==2.3.1
pip install openpyxl==3.1.5
pip install xlrd==2.0.2
```

### AI/LangChain Dependencies
```bash
pip install langchain==0.3.26
pip install langchain-core==0.3.69
pip install langchain-openai==0.3.28
pip install openai==1.54.4
```

### Environment and Utilities
```bash
pip install python-dotenv==1.0.1
```

## Quick Install (All at Once)

You can install all dependencies with a single command:

```bash
pip install Flask==3.0.3 Flask-CORS==4.0.1 Werkzeug==3.0.3 psycopg2-binary==2.9.9 pandas==2.3.1 openpyxl==3.1.5 xlrd==2.0.2 langchain==0.3.26 langchain-core==0.3.69 langchain-openai==0.3.28 openai==1.54.4 python-dotenv==1.0.1
```

## Node.js Dependencies

For the frontend, you'll also need to install Node.js dependencies:

```bash
npm install
```

## Environment Setup

1. Create a `.env.local` file in the root directory
2. Add your environment variables:

```
DATABASE_URL=your_postgresql_connection_string
OPENAI_API_KEY=your_openai_api_key
PGHOST=your_db_host
PGPORT=your_db_port
PGUSER=your_db_user
PGPASSWORD=your_db_password
PGDATABASE=your_db_name
```

## Database Setup

1. Create a PostgreSQL database
2. Run the database setup script:
   ```bash
   psql -f database_setup_complete.sql your_database_name
   ```

## Running the Application

### Development Mode (Recommended)
```bash
npm run dev
```
This starts both the React frontend (port 5000) and Python Flask backend (port 8000).

### Manual Start
If you prefer to run servers separately:

**Frontend:**
```bash
npm run dev:client
```

**Backend:**
```bash
cd server && python simple_flask.py
```

## Access Points

- **Frontend**: http://localhost:5000
- **Backend API**: http://localhost:8000
- **Veritas GPT Chat**: http://localhost:5000/veritas-gpt

## Troubleshooting

### Common Issues

1. **Database Connection Error**: Verify your DATABASE_URL is correct
2. **OpenAI API Error**: Check your OPENAI_API_KEY is valid
3. **Port Already in Use**: Kill existing processes on ports 5000/8000
4. **Module Not Found**: Ensure all pip packages are installed correctly

### Python Version
This application requires Python 3.11 or higher.

### Node.js Version
This application works with Node.js 18+ or 20+.