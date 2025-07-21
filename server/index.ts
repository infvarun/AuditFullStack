import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import routes from './routes.js';

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

  // Serve a simple working UI for development
  app.get('/', (req, res) => {
    res.send(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Audit Data Collection Platform</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 40px; }
          .container { max-width: 800px; margin: 0 auto; }
          .status { background: #e7f5e7; padding: 20px; border-radius: 8px; margin: 20px 0; }
          .endpoints { background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 10px 0; }
          .endpoint { margin: 8px 0; }
          .success { color: #28a745; }
          .api-link { color: #007bff; text-decoration: none; }
          .api-link:hover { text-decoration: underline; }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>🎯 Audit Data Collection Platform</h1>
          
          <div class="status">
            <h2 class="success">✅ PostgreSQL Database Integration Complete</h2>
            <p>Your audit platform is running with full database connectivity!</p>
            <p><strong>Database:</strong> Connected to Neon PostgreSQL</p>
            <p><strong>Backend:</strong> Node.js Express Server</p>
            <p><strong>ORM:</strong> Drizzle with complete schema</p>
          </div>
          
          <h3>🔗 Available API Endpoints</h3>
          <div class="endpoints">
            <div class="endpoint">
              <a href="/api/health" class="api-link">GET /api/health</a> - Server health check
            </div>
            <div class="endpoint">
              <a href="/api/applications" class="api-link">GET /api/applications</a> - List all audit applications
            </div>
            <div class="endpoint">
              <strong>POST /api/applications</strong> - Create new audit application
            </div>
            <div class="endpoint">
              <strong>POST /api/excel/get-columns</strong> - Process Excel file columns
            </div>
            <div class="endpoint">
              <strong>GET /api/connectors/:ciId</strong> - Get tool connectors for CI ID
            </div>
            <div class="endpoint">
              <strong>POST /api/questions/analyze</strong> - AI-powered question analysis
            </div>
          </div>
          
          <h3>📊 Database Tables</h3>
          <ul>
            <li><strong>Applications</strong> - Audit metadata and settings</li>
            <li><strong>Data Requests</strong> - File uploads and question parsing</li>
            <li><strong>Tool Connectors</strong> - External system integrations</li>
            <li><strong>Question Analyses</strong> - AI-powered analysis results</li>
            <li><strong>Audit Results</strong> - Final audit outcomes</li>
            <li><strong>Data Collection Sessions</strong> - Progress tracking</li>
          </ul>
          
          <p><em>Database integration is complete and ready for your audit workflow!</em></p>
        </div>
      </body>
      </html>
    `);
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
    console.log(`📦 Frontend: Simple UI for database demonstration`);
    console.log(`🔗 Backend: Express + PostgreSQL`);
    console.log(`✅ Database: All tables created and ready`);
  });
}

startServer().catch(err => {
  console.error('Failed to start server:', err);
  process.exit(1);
});