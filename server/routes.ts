import express, { Request, Response } from 'express';
import { z } from 'zod';
import { storage } from './storage';
import { 
  insertApplicationSchema,
  insertDataRequestSchema, 
  insertToolConnectorSchema,
  insertDataCollectionSessionSchema,
  insertQuestionAnalysisSchema,
  insertAuditResultSchema
} from '@shared/schema';
import multer from 'multer';
import XLSX from 'xlsx';
import { nanoid } from 'nanoid';

// Extend Request type to include file property
interface MulterRequest extends Request {
  file?: Express.Multer.File;
}

const router = express.Router();

// Configure multer for file uploads
const upload = multer({ 
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 } // 10MB limit
});

// Application routes
router.get('/applications', async (req, res) => {
  try {
    const applications = await storage.getApplications();
    res.json(applications);
  } catch (error) {
    console.error('Error fetching applications:', error);
    res.status(500).json({ error: 'Failed to fetch applications' });
  }
});

router.get('/applications/:id', async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const application = await storage.getApplication(id);
    if (!application) {
      return res.status(404).json({ error: 'Application not found' });
    }
    res.json(application);
  } catch (error) {
    console.error('Error fetching application:', error);
    res.status(500).json({ error: 'Failed to fetch application' });
  }
});

router.post('/applications', async (req, res) => {
  try {
    const validatedData = insertApplicationSchema.parse(req.body);
    const application = await storage.createApplication(validatedData);
    res.json(application);
  } catch (error) {
    console.error('Error creating application:', error);
    if (error instanceof z.ZodError) {
      res.status(400).json({ error: 'Invalid application data', details: error.errors });
    } else {
      res.status(500).json({ error: 'Failed to create application' });
    }
  }
});

router.patch('/applications/:id', async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const updateData = req.body;
    const application = await storage.updateApplication(id, updateData);
    if (!application) {
      return res.status(404).json({ error: 'Application not found' });
    }
    res.json(application);
  } catch (error) {
    console.error('Error updating application:', error);
    res.status(500).json({ error: 'Failed to update application' });
  }
});

// Data request routes
router.get('/data-requests/:applicationId/:fileType', async (req, res) => {
  try {
    const applicationId = parseInt(req.params.applicationId);
    const fileType = req.params.fileType;
    const dataRequest = await storage.getDataRequest(applicationId, fileType);
    res.json(dataRequest);
  } catch (error) {
    console.error('Error fetching data request:', error);
    res.status(500).json({ error: 'Failed to fetch data request' });
  }
});

router.post('/data-requests', async (req, res) => {
  try {
    const validatedData = insertDataRequestSchema.parse(req.body);
    const dataRequest = await storage.createDataRequest(validatedData);
    res.json(dataRequest);
  } catch (error) {
    console.error('Error creating data request:', error);
    if (error instanceof z.ZodError) {
      res.status(400).json({ error: 'Invalid data request data', details: error.errors });
    } else {
      res.status(500).json({ error: 'Failed to create data request' });
    }
  }
});

// Excel file processing routes
router.post('/excel/get-columns', upload.single('file'), async (req: MulterRequest, res: Response) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const workbook = XLSX.read(req.file.buffer, { type: 'buffer' });
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];
    
    const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
    
    if (jsonData.length === 0) {
      return res.status(400).json({ error: 'Empty spreadsheet' });
    }

    const headers = jsonData[0] as string[];
    const sampleData = jsonData.slice(1, 6); // First 5 data rows

    res.json({
      columns: headers,
      sampleData: sampleData,
      totalRows: jsonData.length - 1
    });
  } catch (error) {
    console.error('Error processing Excel file:', error);
    res.status(500).json({ error: 'Failed to process Excel file' });
  }
});

router.post('/excel/process-file', upload.single('file'), async (req: MulterRequest, res: Response) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const { applicationId, fileType, columnMappings } = req.body;
    const mappings = JSON.parse(columnMappings);

    const workbook = XLSX.read(req.file.buffer, { type: 'buffer' });
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];
    
    const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
    const headers = jsonData[0] as string[];
    const dataRows = jsonData.slice(1);

    // Process questions based on column mappings
    const questions: any[] = [];
    const categories = new Set<string>();
    const subcategories = new Set<string>();

    dataRows.forEach((row: unknown, index: number) => {
      const rowArray = row as any[];
      const questionData: any = {
        id: `q_${nanoid(8)}`,
        rowIndex: index + 2, // Excel row number (1-indexed + header)
      };

      // Map columns to question fields
      Object.entries(mappings).forEach(([field, columnIndex]) => {
        if (columnIndex !== null && columnIndex !== undefined && typeof columnIndex === 'number' && columnIndex < rowArray.length) {
          questionData[field] = rowArray[columnIndex];
        }
      });

      // Extract categories and subcategories
      if (questionData.process) {
        categories.add(questionData.process);
      }
      if (questionData.subProcess) {
        subcategories.add(questionData.subProcess);
      }

      questions.push(questionData);
    });

    // Create data request record
    const dataRequestData = {
      applicationId: parseInt(applicationId),
      fileName: req.file.originalname,
      fileSize: req.file.size,
      fileType: fileType,
      questions: questions,
      totalQuestions: questions.length,
      categories: Array.from(categories),
      subcategories: Array.from(subcategories),
      columnMappings: mappings
    };

    const dataRequest = await storage.createDataRequest(dataRequestData);
    res.json(dataRequest);
  } catch (error) {
    console.error('Error processing Excel file:', error);
    res.status(500).json({ error: 'Failed to process Excel file' });
  }
});

// Tool connector routes
router.get('/connectors/:ciId', async (req, res) => {
  try {
    const ciId = req.params.ciId;
    const connectors = await storage.getConnectorsByCiId(ciId);
    res.json(connectors);
  } catch (error) {
    console.error('Error fetching connectors:', error);
    res.status(500).json({ error: 'Failed to fetch connectors' });
  }
});

router.post('/connectors', async (req, res) => {
  try {
    const validatedData = insertToolConnectorSchema.parse(req.body);
    const connector = await storage.createConnector(validatedData);
    res.json(connector);
  } catch (error) {
    console.error('Error creating connector:', error);
    if (error instanceof z.ZodError) {
      res.status(400).json({ error: 'Invalid connector data', details: error.errors });
    } else {
      res.status(500).json({ error: 'Failed to create connector' });
    }
  }
});

router.patch('/connectors/:id', async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const updateData = req.body;
    const connector = await storage.updateConnector(id, updateData);
    if (!connector) {
      return res.status(404).json({ error: 'Connector not found' });
    }
    res.json(connector);
  } catch (error) {
    console.error('Error updating connector:', error);
    res.status(500).json({ error: 'Failed to update connector' });
  }
});

router.delete('/connectors/:id', async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const success = await storage.deleteConnector(id);
    if (!success) {
      return res.status(404).json({ error: 'Connector not found' });
    }
    res.json({ success: true });
  } catch (error) {
    console.error('Error deleting connector:', error);
    res.status(500).json({ error: 'Failed to delete connector' });
  }
});

// Data collection session routes
router.get('/data-collection/:applicationId', async (req, res) => {
  try {
    const applicationId = parseInt(req.params.applicationId);
    const session = await storage.getDataCollectionSession(applicationId);
    res.json(session);
  } catch (error) {
    console.error('Error fetching data collection session:', error);
    res.status(500).json({ error: 'Failed to fetch data collection session' });
  }
});

router.post('/data-collection/start', async (req, res) => {
  try {
    const sessionData = {
      applicationId: req.body.applicationId,
      status: 'running',
      progress: 0,
      logs: [],
      startedAt: new Date()
    };
    
    const session = await storage.createDataCollectionSession(sessionData);
    res.json(session);
  } catch (error) {
    console.error('Error starting data collection:', error);
    res.status(500).json({ error: 'Failed to start data collection' });
  }
});

// Question analysis routes
router.get('/questions/analysis/:applicationId', async (req, res) => {
  try {
    const applicationId = parseInt(req.params.applicationId);
    const analyses = await storage.getQuestionAnalyses(applicationId);
    res.json(analyses);
  } catch (error) {
    console.error('Error fetching question analyses:', error);
    res.status(500).json({ error: 'Failed to fetch question analyses' });
  }
});

router.post('/questions/analyze', async (req, res) => {
  try {
    const { applicationId, questions } = req.body;
    
    // Basic AI analysis simulation (in a real app, integrate with OpenAI or similar)
    const analyses = questions.map((question: any, index: number) => ({
      applicationId,
      questionId: question.id,
      originalQuestion: question.question || question.text,
      category: question.process || 'General',
      subcategory: question.subProcess || null,
      aiPrompt: `Analyze the question: "${question.question || question.text}"`,
      toolSuggestion: determineToolSuggestion(question),
      connectorReason: `Based on the question content and category "${question.process || 'General'}"`,
      connectorToUse: determineConnector(question)
    }));

    const savedAnalyses = await storage.createQuestionAnalyses(analyses);
    res.json(savedAnalyses);
  } catch (error) {
    console.error('Error analyzing questions:', error);
    res.status(500).json({ error: 'Failed to analyze questions' });
  }
});

// Audit results routes
router.get('/audit-results/:applicationId', async (req, res) => {
  try {
    const applicationId = parseInt(req.params.applicationId);
    const results = await storage.getAuditResults(applicationId);
    res.json(results);
  } catch (error) {
    console.error('Error fetching audit results:', error);
    res.status(500).json({ error: 'Failed to fetch audit results' });
  }
});

// Health check
router.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Helper functions for AI analysis
function determineToolSuggestion(question: any): string {
  const text = (question.question || question.text || '').toLowerCase();
  
  if (text.includes('database') || text.includes('sql') || text.includes('table')) {
    return 'SQL Server';
  }
  if (text.includes('email') || text.includes('outlook') || text.includes('exchange')) {
    return 'Outlook';
  }
  if (text.includes('servicenow') || text.includes('snow') || text.includes('ticket')) {
    return 'ServiceNow';
  }
  if (text.includes('file') || text.includes('document') || text.includes('nas')) {
    return 'NAS Path';
  }
  if (text.includes('gnosis') || text.includes('knowledge')) {
    return 'Gnosis Path';
  }
  
  return 'Manual Review';
}

function determineConnector(question: any): string {
  const suggestion = determineToolSuggestion(question);
  
  switch (suggestion) {
    case 'SQL Server':
      return 'sql_server';
    case 'Outlook':
      return 'outlook';
    case 'ServiceNow':
      return 'servicenow';
    case 'NAS Path':
      return 'nas_path';
    case 'Gnosis Path':
      return 'gnosis_path';
    default:
      return 'manual';
  }
}

export default router;