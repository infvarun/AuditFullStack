import { pgTable, text, serial, integer, boolean, timestamp, json, uniqueIndex } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const applications = pgTable("applications", {
  id: serial("id").primaryKey(),
  auditName: text("audit_name").notNull(),
  name: text("name").notNull(),
  ciId: text("ci_id").notNull(),
  startDate: text("start_date").notNull(),
  endDate: text("end_date").notNull(),
  settings: json("settings"),
  status: text("status").default("In Progress"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const dataRequests = pgTable("data_requests", {
  id: serial("id").primaryKey(),
  applicationId: integer("application_id").references(() => applications.id),
  fileName: text("file_name").notNull(),
  fileSize: integer("file_size").notNull(),
  fileType: text("file_type").notNull().default("primary"), // primary or followup
  questions: json("questions").notNull(),
  totalQuestions: integer("total_questions").notNull(),
  categories: json("categories").notNull(),
  subcategories: json("subcategories").notNull(),
  columnMappings: json("column_mappings").notNull(),
  uploadedAt: timestamp("uploaded_at").defaultNow(),
}, (table) => ({
  uniqueApplicationFileType: uniqueIndex("unique_application_file_type").on(table.applicationId, table.fileType),
}));

export const toolConnectors = pgTable("tool_connectors", {
  id: serial("id").primaryKey(),
  applicationId: integer("application_id").references(() => applications.id),
  ciId: text("ci_id").notNull(),
  connectorType: text("connector_type").notNull(),
  configuration: json("configuration").notNull(),
  status: text("status").notNull().default("pending"),
  createdAt: timestamp("created_at").defaultNow(),
}, (table) => ({
  uniqueCiConnectorType: uniqueIndex("unique_ci_connector_type").on(table.ciId, table.connectorType),
}));

export const dataCollectionSessions = pgTable("data_collection_sessions", {
  id: serial("id").primaryKey(),
  applicationId: integer("application_id").references(() => applications.id),
  status: text("status").notNull().default("pending"),
  progress: integer("progress").notNull().default(0),
  logs: json("logs").notNull().default([]),
  startedAt: timestamp("started_at"),
  completedAt: timestamp("completed_at"),
});

export const questionAnalyses = pgTable("question_analyses", {
  id: serial("id").primaryKey(),
  applicationId: integer("application_id").references(() => applications.id),
  questionId: text("question_id").notNull(),
  originalQuestion: text("original_question").notNull(),
  category: text("category").notNull(),
  subcategory: text("subcategory"),
  aiPrompt: text("ai_prompt").notNull(),
  toolSuggestion: text("tool_suggestion").notNull(),
  connectorReason: text("connector_reason").notNull(),
  connectorToUse: text("connector_to_use").notNull(),
  createdAt: timestamp("created_at").defaultNow(),
}, (table) => ({
  uniqueApplicationQuestion: uniqueIndex("unique_application_question").on(table.applicationId, table.questionId),
}));

export const auditResults = pgTable("audit_results", {
  id: serial("id").primaryKey(),
  applicationId: integer("application_id").references(() => applications.id),
  sessionId: integer("session_id").references(() => dataCollectionSessions.id),
  questionId: text("question_id").notNull(),
  question: text("question").notNull(),
  category: text("category").notNull(),
  status: text("status").notNull(),
  documentPath: text("document_path"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const insertApplicationSchema = createInsertSchema(applications).omit({
  id: true,
  createdAt: true,
});

export const insertDataRequestSchema = createInsertSchema(dataRequests).omit({
  id: true,
  uploadedAt: true,
});

export const insertToolConnectorSchema = createInsertSchema(toolConnectors).omit({
  id: true,
  createdAt: true,
});

export const insertDataCollectionSessionSchema = createInsertSchema(dataCollectionSessions).omit({
  id: true,
  startedAt: true,
  completedAt: true,
});

export const insertQuestionAnalysisSchema = createInsertSchema(questionAnalyses).omit({
  id: true,
  createdAt: true,
});

export const insertAuditResultSchema = createInsertSchema(auditResults).omit({
  id: true,
  createdAt: true,
});

export type Application = typeof applications.$inferSelect;
export type InsertApplication = z.infer<typeof insertApplicationSchema>;
export type DataRequest = typeof dataRequests.$inferSelect;
export type InsertDataRequest = z.infer<typeof insertDataRequestSchema>;
export type QuestionAnalysis = typeof questionAnalyses.$inferSelect;
export type InsertQuestionAnalysis = z.infer<typeof insertQuestionAnalysisSchema>;
export type ToolConnector = typeof toolConnectors.$inferSelect;
export type InsertToolConnector = z.infer<typeof insertToolConnectorSchema>;
export type DataCollectionSession = typeof dataCollectionSessions.$inferSelect;
export type InsertDataCollectionSession = z.infer<typeof insertDataCollectionSessionSchema>;
export type AuditResult = typeof auditResults.$inferSelect;
export type InsertAuditResult = z.infer<typeof insertAuditResultSchema>;
