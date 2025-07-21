# Development Guide

## Architecture Overview

This application uses a clean separation architecture:
- **React + Vite Frontend** (port 5000)
- **Python Flask Backend** (port 8000)

## Running the Application

### Option 1: Both Servers Together (Recommended)
```bash
npm run dev
```
This starts both React and Flask servers using concurrently.

### Option 2: Individual Servers

#### React Frontend Only
```bash
# Terminal 1
npm run vite --host 0.0.0.0 --port 5000
```

#### Flask Backend Only
```bash
# Terminal 2
cd server && python app.py
```

### Option 3: Using Shell Scripts
```bash
# Both servers
./start_both.sh

# React only
./start_react.sh

# Flask only
./start_flask.sh
```

## API Endpoints

The Flask backend provides these endpoints:

- `GET /health` - Health check
- `GET /api/applications` - Get all applications
- `POST /api/applications` - Create new application
- `GET /api/applications/{id}` - Get specific application
- `POST /api/excel/get-columns` - Analyze Excel file columns
- `POST /api/excel/process` - Process Excel file with mappings

## Development URLs

- **React Frontend**: http://localhost:5000
- **Flask Backend**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

## CORS Configuration

Flask-CORS is configured to allow requests from:
- http://localhost:5000
- http://0.0.0.0:5000

## Database Connection

The Flask backend connects to PostgreSQL using environment variables:
- `DATABASE_URL` (recommended)
- Or individual: `PGHOST`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGPORT`