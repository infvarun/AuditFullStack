import { 
  applications, 
  dataRequests,
  toolConnectors,
  dataCollectionSessions,
  questionAnalyses,
  auditResults,
  type Application, 
  type InsertApplication,
  type DataRequest,
  type InsertDataRequest,
  type ToolConnector,
  type InsertToolConnector,
  type DataCollectionSession,
  type InsertDataCollectionSession,
  type QuestionAnalysis,
  type InsertQuestionAnalysis,
  type AuditResult,
  type InsertAuditResult
} from "@shared/schema";
import { db } from "./db";
import { eq, and } from "drizzle-orm";

export interface IStorage {
  // Application operations
  getApplications(): Promise<Application[]>;
  getApplication(id: number): Promise<Application | undefined>;
  createApplication(insertApplication: InsertApplication): Promise<Application>;
  updateApplication(id: number, updateData: Partial<InsertApplication>): Promise<Application | undefined>;
  
  // Data request operations
  getDataRequest(applicationId: number, fileType: string): Promise<DataRequest | undefined>;
  createDataRequest(insertDataRequest: InsertDataRequest): Promise<DataRequest>;
  updateDataRequest(id: number, updateData: Partial<InsertDataRequest>): Promise<DataRequest | undefined>;
  
  // Tool connector operations
  getConnectorsByCiId(ciId: string): Promise<ToolConnector[]>;
  getConnector(id: number): Promise<ToolConnector | undefined>;
  createConnector(insertConnector: InsertToolConnector): Promise<ToolConnector>;
  updateConnector(id: number, updateData: Partial<InsertToolConnector>): Promise<ToolConnector | undefined>;
  deleteConnector(id: number): Promise<boolean>;
  
  // Data collection session operations
  getDataCollectionSession(applicationId: number): Promise<DataCollectionSession | undefined>;
  createDataCollectionSession(insertSession: InsertDataCollectionSession): Promise<DataCollectionSession>;
  updateDataCollectionSession(id: number, updateData: Partial<InsertDataCollectionSession>): Promise<DataCollectionSession | undefined>;
  
  // Question analysis operations
  getQuestionAnalyses(applicationId: number): Promise<QuestionAnalysis[]>;
  createQuestionAnalyses(analyses: InsertQuestionAnalysis[]): Promise<QuestionAnalysis[]>;
  updateQuestionAnalysis(id: number, updateData: Partial<InsertQuestionAnalysis>): Promise<QuestionAnalysis | undefined>;
  
  // Audit result operations
  getAuditResults(applicationId: number): Promise<AuditResult[]>;
  createAuditResult(insertResult: InsertAuditResult): Promise<AuditResult>;
}

export class DatabaseStorage implements IStorage {
  async getApplications(): Promise<Application[]> {
    return await db.select().from(applications);
  }

  async getApplication(id: number): Promise<Application | undefined> {
    const [application] = await db.select().from(applications).where(eq(applications.id, id));
    return application || undefined;
  }

  async createApplication(insertApplication: InsertApplication): Promise<Application> {
    const [application] = await db
      .insert(applications)
      .values(insertApplication)
      .returning();
    return application;
  }

  async updateApplication(id: number, updateData: Partial<InsertApplication>): Promise<Application | undefined> {
    const [application] = await db
      .update(applications)
      .set(updateData)
      .where(eq(applications.id, id))
      .returning();
    return application || undefined;
  }

  async getDataRequest(applicationId: number, fileType: string): Promise<DataRequest | undefined> {
    const [dataRequest] = await db
      .select()
      .from(dataRequests)
      .where(and(eq(dataRequests.applicationId, applicationId), eq(dataRequests.fileType, fileType)));
    return dataRequest || undefined;
  }

  async createDataRequest(insertDataRequest: InsertDataRequest): Promise<DataRequest> {
    const [dataRequest] = await db
      .insert(dataRequests)
      .values(insertDataRequest)
      .returning();
    return dataRequest;
  }

  async updateDataRequest(id: number, updateData: Partial<InsertDataRequest>): Promise<DataRequest | undefined> {
    const [dataRequest] = await db
      .update(dataRequests)
      .set(updateData)
      .where(eq(dataRequests.id, id))
      .returning();
    return dataRequest || undefined;
  }

  async getConnectorsByCiId(ciId: string): Promise<ToolConnector[]> {
    return await db.select().from(toolConnectors).where(eq(toolConnectors.ciId, ciId));
  }

  async getConnector(id: number): Promise<ToolConnector | undefined> {
    const [connector] = await db.select().from(toolConnectors).where(eq(toolConnectors.id, id));
    return connector || undefined;
  }

  async createConnector(insertConnector: InsertToolConnector): Promise<ToolConnector> {
    const [connector] = await db
      .insert(toolConnectors)
      .values(insertConnector)
      .returning();
    return connector;
  }

  async updateConnector(id: number, updateData: Partial<InsertToolConnector>): Promise<ToolConnector | undefined> {
    const [connector] = await db
      .update(toolConnectors)
      .set(updateData)
      .where(eq(toolConnectors.id, id))
      .returning();
    return connector || undefined;
  }

  async deleteConnector(id: number): Promise<boolean> {
    const result = await db.delete(toolConnectors).where(eq(toolConnectors.id, id));
    return result.rowCount > 0;
  }

  async getDataCollectionSession(applicationId: number): Promise<DataCollectionSession | undefined> {
    const [session] = await db
      .select()
      .from(dataCollectionSessions)
      .where(eq(dataCollectionSessions.applicationId, applicationId));
    return session || undefined;
  }

  async createDataCollectionSession(insertSession: InsertDataCollectionSession): Promise<DataCollectionSession> {
    const [session] = await db
      .insert(dataCollectionSessions)
      .values(insertSession)
      .returning();
    return session;
  }

  async updateDataCollectionSession(id: number, updateData: Partial<InsertDataCollectionSession>): Promise<DataCollectionSession | undefined> {
    const [session] = await db
      .update(dataCollectionSessions)
      .set(updateData)
      .where(eq(dataCollectionSessions.id, id))
      .returning();
    return session || undefined;
  }

  async getQuestionAnalyses(applicationId: number): Promise<QuestionAnalysis[]> {
    return await db.select().from(questionAnalyses).where(eq(questionAnalyses.applicationId, applicationId));
  }

  async createQuestionAnalyses(analyses: InsertQuestionAnalysis[]): Promise<QuestionAnalysis[]> {
    const results = await db
      .insert(questionAnalyses)
      .values(analyses)
      .returning();
    return results;
  }

  async updateQuestionAnalysis(id: number, updateData: Partial<InsertQuestionAnalysis>): Promise<QuestionAnalysis | undefined> {
    const [analysis] = await db
      .update(questionAnalyses)
      .set(updateData)
      .where(eq(questionAnalyses.id, id))
      .returning();
    return analysis || undefined;
  }

  async getAuditResults(applicationId: number): Promise<AuditResult[]> {
    return await db.select().from(auditResults).where(eq(auditResults.applicationId, applicationId));
  }

  async createAuditResult(insertResult: InsertAuditResult): Promise<AuditResult> {
    const [result] = await db
      .insert(auditResults)
      .values(insertResult)
      .returning();
    return result;
  }
}

export const storage = new DatabaseStorage();