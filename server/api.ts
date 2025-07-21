import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import routes from './routes.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = parseInt(process.env.API_PORT || '3001');

// Middleware
app.use(cors({
  origin: ['http://localhost:5173', 'http://localhost:5000', 'http://0.0.0.0:5173', 'http://0.0.0.0:5000'],
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// API routes
app.use(routes);

// Health check at root for API server
app.get('/', (req, res) => {
  res.json({ 
    status: 'API server running', 
    timestamp: new Date().toISOString(),
    endpoints: ['/api/health', '/api/applications', '/api/data-requests', '/api/connectors'] 
  });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`🔗 Express API server running on http://0.0.0.0:${PORT}`);
});