#!/bin/bash
echo "🚀 Starting both React frontend and Flask backend..."
echo "📦 React will run on http://localhost:5000"
echo "🔗 Flask will run on http://localhost:8000"

# Start both servers concurrently
npx concurrently \
  "npx vite --host 0.0.0.0 --port 5000" \
  "cd server && python app.py" \
  --names "React,Flask" \
  --prefix-colors "cyan,yellow"