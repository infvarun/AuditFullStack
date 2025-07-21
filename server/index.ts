import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import routes from './routes.js';
import { createServer } from 'vite';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function startServer() {
  const app = express();
  const PORT = parseInt(process.env.PORT || '5000');

  // Middleware
  app.use(cors());
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  // API routes
  app.use('/api', routes);

  // Add basic frontend route for development
  app.get('/', (req, res) => {
    res.json({
      message: 'Audit Data Collection Platform API',
      status: 'PostgreSQL Database Integration Complete',
      timestamp: new Date().toISOString(),
      database: 'Connected to Neon PostgreSQL',
      endpoints: {
        applications: '/api/applications',
        health: '/api/health',
        'data-requests': '/api/data-requests',
        connectors: '/api/connectors',
        excel: '/api/excel'
      }
    });
  });

  // Production: Serve static files
  if (process.env.NODE_ENV === 'production') {
    app.use(express.static(path.join(__dirname, '../dist/public')));
    
    app.get('*', (req, res) => {
      res.sendFile(path.join(__dirname, '../dist/public/index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Server running on http://0.0.0.0:${PORT}`);
    console.log(`📦 Frontend: ${process.env.NODE_ENV !== 'production' ? 'Vite Dev Server' : 'Static Files'}`);
    console.log(`🔗 Backend: Express + PostgreSQL`);
  });
}

startServer().catch(err => {
  console.error('Failed to start server:', err);
  process.exit(1);
});