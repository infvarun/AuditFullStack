import { useState, useEffect } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Brain, CheckCircle, Settings, Save, RefreshCw, Database, FileText, Bug, Clipboard, TestTube, Wrench } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";
import { Separator } from "../ui/separator";
import { Progress } from "../ui/progress";
import { apiRequest, queryClient } from "../../lib/queryClient";
import { useToast } from "../../hooks/use-toast";

interface StepThreeProps {
  applicationId: number | null;
  onNext: () => void;
  setCanProceed: (canProceed: boolean) => void;
}

interface Question {
  id: string;
  questionNumber: string;
  process: string;
  subProcess: string;
  question: string;
}

interface QuestionAnalysis {
  questionId: string;
  originalQuestion: string;
  category: string;
  subcategory: string;
  aiPrompt: string;
  toolSuggestion: string | string[]; // Can be single tool or multiple tools
  connectorReason: string;
  connectorToUse: string | string[]; // Can be single or multiple connectors
}

interface ToolConnector {
  id: number;
  connector_type: string;
  ciId: string;
  configuration: any;
  status: string;
}

const AVAILABLE_TOOLS = [
  { id: 'SQL Server DB', name: 'SQL Server DB', icon: Database },
  { id: 'Oracle DB', name: 'Oracle DB', icon: Database },
  { id: 'Gnosis Document Repository', name: 'Gnosis Document Repository', icon: FileText },
  { id: 'Jira', name: 'Jira', icon: Bug },
  { id: 'QTest', name: 'QTest', icon: TestTube },
  { id: 'ServiceNow', name: 'ServiceNow', icon: Wrench },
];

// Map old tool IDs to new ones for backward compatibility
const TOOL_ID_MAPPING: Record<string, string> = {
  'sql_server': 'SQL Server DB',
  'oracle_db': 'Oracle DB', 
  'gnosis': 'Gnosis Document Repository',
  'jira': 'Jira',
  'qtest': 'QTest',
  'service_now': 'ServiceNow',
};

export default function StepThree({ applicationId, onNext, setCanProceed }: StepThreeProps) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [analyses, setAnalyses] = useState<QuestionAnalysis[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [isSaved, setIsSaved] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  const { toast } = useToast();

  // Get application data
  const { data: applicationData } = useQuery<any>({
    queryKey: [`/api/applications/${applicationId}`],
    enabled: !!applicationId,
  });

  // Get data requests (questions from uploaded files)
  const { data: dataRequests, isLoading } = useQuery({
    queryKey: ["/api/data-requests/application", applicationId],
    enabled: !!applicationId,
  });

  // Get available connectors for this CI
  const { data: connectors = [] } = useQuery<ToolConnector[]>({
    queryKey: [`/api/connectors/ci/${applicationData?.ciId}`],
    enabled: !!applicationData?.ciId,
  });

  // Get existing question analyses
  const { data: existingAnalyses, refetch: refetchAnalyses } = useQuery<QuestionAnalysis[]>({
    queryKey: [`/api/questions/analyses/${applicationId}`],
    enabled: !!applicationId,
  });

  // Extract questions from data requests
  useEffect(() => {
    if (dataRequests && Array.isArray(dataRequests)) {
      const allQuestions: Question[] = [];
      dataRequests.forEach((request: any) => {
        if (request.questions) {
          const parsedQuestions = typeof request.questions === 'string' 
            ? JSON.parse(request.questions) 
            : request.questions;
          allQuestions.push(...parsedQuestions);
        }
      });
      setQuestions(allQuestions);
    }
  }, [dataRequests]);

  // Load existing analyses and convert old tool IDs to new ones
  useEffect(() => {
    if (existingAnalyses && existingAnalyses.length > 0) {
      const updatedAnalyses = existingAnalyses.map(analysis => {
        // Handle both single and multiple tool suggestions
        let updatedToolSuggestion;
        if (Array.isArray(analysis.toolSuggestion)) {
          updatedToolSuggestion = analysis.toolSuggestion.map(tool => TOOL_ID_MAPPING[tool] || tool);
        } else {
          updatedToolSuggestion = TOOL_ID_MAPPING[analysis.toolSuggestion] || analysis.toolSuggestion;
        }
        
        let updatedConnectorToUse;
        if (Array.isArray(analysis.connectorToUse)) {
          updatedConnectorToUse = analysis.connectorToUse.map(connector => TOOL_ID_MAPPING[connector] || connector);
        } else {
          updatedConnectorToUse = TOOL_ID_MAPPING[analysis.connectorToUse] || analysis.connectorToUse;
        }
        
        return {
          ...analysis,
          toolSuggestion: updatedToolSuggestion,
          connectorToUse: updatedConnectorToUse
        };
      });
      setAnalyses(updatedAnalyses);
      setIsSaved(true);
      setCanProceed(true);
    }
  }, [existingAnalyses, setCanProceed]);

  // Check if we can proceed - handle both single and multiple tool selections
  useEffect(() => {
    const hasAnalyses = analyses.length > 0;
    const allQuestionsConfigured = analyses.every(analysis => {
      const toolSuggestions = Array.isArray(analysis.toolSuggestion) 
        ? analysis.toolSuggestion 
        : [analysis.toolSuggestion];
      
      return toolSuggestions.every(tool => {
        const connectorExists = connectors.some(c => c.connector_type === (TOOL_ID_MAPPING[tool] || tool));
        return connectorExists && tool && tool.trim() !== '';
      });
    });
    setCanProceed(hasAnalyses && allQuestionsConfigured && isSaved);
  }, [analyses, connectors, isSaved, setCanProceed]);

  // AI Question Analysis Mutation with proper progress tracking
  const analyzeQuestionsMutation = useMutation({
    mutationFn: async (questions: Question[]) => {
      const totalQuestions = questions.length;
      let processedCount = 0;
      const analyses: any[] = [];
      
      // Process questions one by one to show proper progress
      for (const question of questions) {
        try {
          const response = await apiRequest("POST", "/api/questions/analyze", {
            applicationId,
            questions: [question] // Send one question at a time
          });
          
          const result = await response.json();
          if (result.analyses && result.analyses.length > 0) {
            analyses.push(result.analyses[0]);
          }
          
          processedCount++;
          const progressPercent = Math.round((processedCount / totalQuestions) * 100);
          setAnalysisProgress(progressPercent);
          
          // Small delay to show progress visually
          await new Promise(resolve => setTimeout(resolve, 100));
          
        } catch (error) {
          console.error(`Error analyzing question ${question.id}:`, error);
          // Add fallback analysis for failed questions
          analyses.push({
            questionId: question.id || '',
            originalQuestion: question.question || '',
            category: question.process || 'General',
            subcategory: question.subProcess || 'Unknown',
            aiPrompt: `Analyze audit question: ${question.question || ''}`,
            toolSuggestion: 'SQL Server DB',
            connectorReason: 'Fallback due to analysis error',
            connectorToUse: 'SQL Server DB'
          });
          
          processedCount++;
          const progressPercent = Math.round((processedCount / totalQuestions) * 100);
          setAnalysisProgress(progressPercent);
        }
      }
      
      return { analyses, total: analyses.length };
    },
    onSuccess: (data) => {
      setAnalyses(data.analyses || []);
      setIsAnalyzing(false);
      setAnalysisProgress(100);
      setHasUnsavedChanges(true);
      setIsSaved(false);
      toast({
        title: "Analysis Complete",
        description: `${data.analyses?.length || 0} questions analyzed successfully`,
      });
    },
    onError: (error) => {
      setIsAnalyzing(false);
      setAnalysisProgress(0);
      toast({
        title: "Analysis Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  // Save analyses mutation
  const saveAnalysesMutation = useMutation({
    mutationFn: async (analyses: QuestionAnalysis[]) => {
      const response = await apiRequest("POST", "/api/questions/analyses/save", {
        applicationId: applicationId,
        analyses: analyses
      });
      return response.json();
    },
    onSuccess: () => {
      setIsSaved(true);
      setHasUnsavedChanges(false);
      toast({
        title: "Analyses Saved",
        description: "Question analyses have been saved successfully",
      });
      refetchAnalyses();
    },
    onError: (error) => {
      toast({
        title: "Save Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const startAnalysis = () => {
    setIsAnalyzing(true);
    setAnalysisProgress(0);
    
    // Start analysis without fake progress - real progress will be tracked in mutation
    analyzeQuestionsMutation.mutate(questions);
  };

  const handleToolChange = (questionId: string, newTool: string, index: number) => {
    setAnalyses(prev => prev.map((analysis, idx) => 
      idx === index 
        ? { 
            ...analysis, 
            toolSuggestion: newTool, 
            connectorToUse: Array.isArray(analysis.toolSuggestion) ? [] : "" // Reset connector selection when tool changes
          }
        : analysis
    ));
    setHasUnsavedChanges(true);
    setIsSaved(false);
  };

  // Handle connector changes for both single and multiple tool scenarios
  const handleConnectorChange = (questionId: string, connectorName: string, index: number) => {
    setAnalyses(prev => prev.map((analysis, idx) => 
      idx === index 
        ? { 
            ...analysis, 
            connectorToUse: Array.isArray(analysis.toolSuggestion) 
              ? analysis.toolSuggestion // For multiple tools, use all tool names
              : analysis.toolSuggestion // For single tool, use the tool name
          }
        : analysis
    ));
    setHasUnsavedChanges(true);
    setIsSaved(false);
  };

  const getConnectorStatus = (toolType: string) => {
    const connector = connectors.find(c => c.connector_type === toolType);
    return { 
      available: !!connector, 
      status: connector?.status || 'not_configured'
    };
  };

  const getToolIcon = (toolType: string) => {
    const tool = AVAILABLE_TOOLS.find(t => t.id === toolType);
    return tool?.icon || Database;
  };

  const getToolName = (toolType: string) => {
    const tool = AVAILABLE_TOOLS.find(t => t.id === toolType);
    return tool?.name || toolType;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-purple-600" />
          <p className="text-slate-600">Loading questions...</p>
        </div>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <Card className="card-modern">
        <CardHeader>
          <CardTitle className="flex items-center space-x-3">
            <Brain className="h-5 w-5 text-purple-600" />
            <span>Question Analysis</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <FileText className="h-12 w-12 text-slate-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-900 mb-2">No Questions Found</h3>
            <p className="text-slate-600">
              Please upload and process Excel files in Step 2 before proceeding with question analysis.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <Card className="card-modern">
        <CardHeader>
          <CardTitle className="flex items-center space-x-3">
            <Brain className="h-5 w-5 text-purple-600" />
            <span className="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              AI-Powered Question Analysis
            </span>
          </CardTitle>
          <p className="text-sm text-slate-600">
            Analyze {questions.length} questions to determine appropriate tools and data collection methods
          </p>
        </CardHeader>
        
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                onClick={startAnalysis}
                disabled={isAnalyzing || analyzeQuestionsMutation.isPending}
                className="btn-gradient"
              >
                {isAnalyzing ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Brain className="h-4 w-4 mr-2" />
                    {analyses.length > 0 ? 'Re-analyze Questions' : 'Analyze Questions'}
                  </>
                )}
              </Button>
              
              {analyses.length > 0 && (
                <Button
                  onClick={() => saveAnalysesMutation.mutate(analyses)}
                  disabled={!hasUnsavedChanges || saveAnalysesMutation.isPending}
                  variant={isSaved ? "outline" : "default"}
                  className={isSaved ? "border-green-500 text-green-700" : ""}
                >
                  {isSaved ? (
                    <>
                      <CheckCircle className="h-4 w-4 mr-2 text-green-600" />
                      Saved
                    </>
                  ) : (
                    <>
                      <Save className="h-4 w-4 mr-2" />
                      Save Changes
                    </>
                  )}
                </Button>
              )}
            </div>
            
            <div className="flex items-center space-x-2 text-sm text-slate-600">
              <span>{questions.length} questions</span>
              {analyses.length > 0 && (
                <>
                  <span>•</span>
                  <span>{analyses.length} analyzed</span>
                </>
              )}
            </div>
          </div>
          
          {/* Progress Bar */}
          {isAnalyzing && (
            <div className="mt-4">
              <div className="flex items-center justify-between text-sm text-slate-600 mb-2">
                <span>Analyzing questions with AI...</span>
                <span>{analysisProgress}%</span>
              </div>
              <Progress value={analysisProgress} className="h-2" />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analyses.length > 0 && (
        <Card className="card-modern">
          <CardHeader>
            <CardTitle className="flex items-center space-x-3">
              <Clipboard className="h-5 w-5 text-green-600" />
              <span>Question Analysis Results</span>
            </CardTitle>
            <p className="text-sm text-slate-600">
              Review and adjust tool suggestions for each question
            </p>
          </CardHeader>
          
          <CardContent>
            <div className="space-y-4">
              {analyses.map((analysis, index) => {
                // Handle status for multiple tools - check if any tool has a connector
                const hasAnyConnector = Array.isArray(analysis.toolSuggestion) 
                  ? analysis.toolSuggestion.some(tool => getConnectorStatus(tool).available)
                  : getConnectorStatus(analysis.toolSuggestion).available;
                const ToolIcon = Array.isArray(analysis.toolSuggestion) 
                  ? getToolIcon(analysis.toolSuggestion[0]) 
                  : getToolIcon(analysis.toolSuggestion);
                
                // Create unique key using multiple fields
                const uniqueKey = `analysis-${applicationId}-${index}-${analysis.questionId || index}-${analysis.originalQuestion?.slice(0, 20) || ''}`;
                
                return (
                  <div key={uniqueKey} className="border border-slate-200 rounded-lg p-4">
                    <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
                      {/* Question ID */}
                      <div>
                        <label className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                          Question ID
                        </label>
                        <p className="mt-1 font-mono text-sm text-slate-900">
                          {analysis.questionId || `Q${index + 1}`}
                        </p>
                      </div>
                      
                      {/* Question */}
                      <div>
                        <label className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                          Question
                        </label>
                        <p className="mt-1 text-sm text-slate-900 line-clamp-2">
                          {analysis.originalQuestion}
                        </p>
                      </div>
                      
                      {/* AI Prompt */}
                      <div>
                        <label className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                          Agent Prompt
                        </label>
                        <p className="mt-1 text-sm text-slate-600 line-clamp-2">
                          {analysis.aiPrompt}
                        </p>
                      </div>
                      
                      {/* Tool Selection - Handle both single and multiple tools */}
                      <div>
                        <label className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                          Tool(s) To Use
                        </label>
                        <div className="mt-1 space-y-2">
                          {Array.isArray(analysis.toolSuggestion) ? (
                            // Multiple tools - show as badges
                            <div className="flex flex-wrap gap-2">
                              {analysis.toolSuggestion.map((tool, toolIndex) => {
                                const toolConfig = AVAILABLE_TOOLS.find(t => t.id === tool || t.id === TOOL_ID_MAPPING[tool]);
                                const Icon = toolConfig?.icon || Database;
                                const connectorStatus = getConnectorStatus(tool);
                                
                                return (
                                  <Badge 
                                    key={`${tool}-${toolIndex}`} 
                                    variant={connectorStatus.available ? "default" : "destructive"}
                                    className="flex items-center space-x-1 px-3 py-1"
                                  >
                                    <Icon className="h-3 w-3" />
                                    <span className="text-xs">{toolConfig?.name || tool}</span>
                                  </Badge>
                                );
                              })}
                            </div>
                          ) : (
                            // Single tool - show as dropdown
                            <Select 
                              value={TOOL_ID_MAPPING[analysis.toolSuggestion] || analysis.toolSuggestion} 
                              onValueChange={(value) => handleToolChange(analysis.questionId, value, index)}
                            >
                              <SelectTrigger>
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                {AVAILABLE_TOOLS.map(tool => {
                                  const Icon = tool.icon;
                                  return (
                                    <SelectItem key={tool.id} value={tool.id}>
                                      <div className="flex items-center space-x-2">
                                        <Icon className="h-4 w-4" />
                                        <span>{tool.name}</span>
                                      </div>
                                    </SelectItem>
                                  );
                                })}
                              </SelectContent>
                            </Select>
                          )}
                        </div>
                      </div>
                      
                      {/* Connector Status - Handle multiple tools */}
                      <div>
                        <label className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                          Connector Status
                        </label>
                        <div className="mt-1 space-y-1">
                          {Array.isArray(analysis.toolSuggestion) ? (
                            // Multiple tools - show status for each
                            analysis.toolSuggestion.map((tool, toolIndex) => {
                              const connectorStatus = getConnectorStatus(tool);
                              return (
                                <div key={`${tool}-status-${toolIndex}`} className="flex items-center justify-between">
                                  <span className="text-xs text-slate-600">{getToolName(tool)}:</span>
                                  {connectorStatus.available ? (
                                    <Badge variant="default" className="bg-green-100 text-green-800 border-green-200 text-xs">
                                      <CheckCircle className="h-3 w-3 mr-1" />
                                      Connected
                                    </Badge>
                                  ) : (
                                    <Badge variant="destructive" className="text-xs">
                                      <Settings className="h-3 w-3 mr-1" />
                                      Not Configured
                                    </Badge>
                                  )}
                                </div>
                              );
                            })
                          ) : (
                            // Single tool - show single status
                            (() => {
                              const connectorStatus = getConnectorStatus(analysis.toolSuggestion);
                              return connectorStatus.available ? (
                                <Badge variant="default" className="bg-green-100 text-green-800 border-green-200">
                                  <CheckCircle className="h-3 w-3 mr-1" />
                                  Connected
                                </Badge>
                              ) : (
                                <div>
                                  <Badge variant="destructive">
                                    <Settings className="h-3 w-3 mr-1" />
                                    Not Configured
                                  </Badge>
                                  <p className="text-xs text-slate-500 mt-1">
                                    Create {getToolName(analysis.toolSuggestion)} connectors in Settings → CI Connectors
                                  </p>
                                </div>
                              );
                            })()
                          )}
                        </div>
                      </div>
                    </div>
                    
                    {/* Expandable Details */}
                    <details className="mt-3">
                      <summary className="cursor-pointer text-sm text-purple-600 hover:text-purple-800">
                        View Analysis Details
                      </summary>
                      <div className="mt-2 p-3 bg-slate-50 rounded border text-sm">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <p className="font-medium text-slate-700">Category:</p>
                            <p className="text-slate-600">{analysis.category}</p>
                          </div>
                          <div>
                            <p className="font-medium text-slate-700">Subcategory:</p>
                            <p className="text-slate-600">{analysis.subcategory}</p>
                          </div>
                          <div className="md:col-span-2">
                            <p className="font-medium text-slate-700">Connector Reasoning:</p>
                            <p className="text-slate-600">{analysis.connectorReason}</p>
                          </div>
                        </div>
                      </div>
                    </details>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}