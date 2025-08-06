import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { TrendingUp, CheckCircle, Clock, XCircle, CircleHelp, FileText, Download, FolderOpen, Eye } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../ui/table";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "../ui/alert-dialog";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";
import { ScrollArea } from "../ui/scroll-area";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";

interface StepFiveProps {
  applicationId: number | null;
  setCanProceed: (canProceed: boolean) => void;
}

export default function StepFive({ applicationId, setCanProceed }: StepFiveProps) {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [selectedAnswer, setSelectedAnswer] = useState<any>(null);

  // Get saved answers from Step 4 execution
  const { data: savedAnswers = [], isLoading } = useQuery({
    queryKey: [`/api/questions/answers/${applicationId}`],
    enabled: !!applicationId,
  });

  // Get original question analyses for display
  const { data: analyses = [] } = useQuery({
    queryKey: [`/api/questions/analyses/${applicationId}`],
    enabled: !!applicationId,
  });

  // Get application data
  const { data: applicationData = {} } = useQuery({
    queryKey: [`/api/applications/${applicationId}`],
    enabled: !!applicationId,
  });

  // Mutation to complete audit
  const completeAuditMutation = useMutation({
    mutationFn: async () => {
      const response = await apiRequest("PUT", `/api/applications/${applicationId}`, {
        status: "Completed"
      });
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Audit Completed",
        description: "The audit has been successfully marked as completed.",
      });
      // Invalidate and refetch application data
      queryClient.invalidateQueries({ queryKey: [`/api/applications/${applicationId}`] });
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: "Failed to complete audit. Please try again.",
        variant: "destructive",
      });
    }
  });

  // Mutation to reset audit status
  const resetAuditMutation = useMutation({
    mutationFn: async () => {
      const response = await apiRequest("PUT", `/api/applications/${applicationId}`, {
        status: "In Progress"
      });
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Status Reset",
        description: "The audit status has been reset to 'In Progress'.",
      });
      // Invalidate and refetch application data
      queryClient.invalidateQueries({ queryKey: [`/api/applications/${applicationId}`] });
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: "Failed to reset audit status. Please try again.",
        variant: "destructive",
      });
    }
  });

  // Step 5 is the final step, no next button needed
  // Always allow proceeding (validation removed)
  useEffect(() => {
    setCanProceed(true);
  }, [setCanProceed]);

  // Calculate statistics from saved answers
  const completed = (savedAnswers as any[]).length;
  const partial = 0; // We don't have partial status in current implementation
  const failed = (analyses as any[]).length - completed;
  const total = (analyses as any[]).length;

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "partial":
        return <Clock className="h-4 w-4 text-yellow-600" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-red-600" />;
      default:
        return <CircleHelp className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusBadge = (hasAnswer: boolean) => {
    if (hasAnswer) {
      return <Badge className="bg-green-100 text-green-800">Completed</Badge>;
    } else {
      return <Badge className="bg-red-100 text-red-800">Failed</Badge>;
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-8">
        <Card>
          <CardContent className="p-6">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
              <p className="mt-4 text-sm text-slate-600">Loading results...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-3">
            <TrendingUp className="h-5 w-5 text-success" />
            <span>Data Collection Results</span>
          </CardTitle>
          <p className="text-sm text-slate-600">
            Review collected data and generated documents
          </p>
        </CardHeader>
        
        <CardContent>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center">
                <CircleHelp className="h-5 w-5 text-blue-600 mr-2" />
                <span className="text-sm font-medium text-blue-900">
                  Total Questions
                </span>
              </div>
              <p className="text-2xl font-bold text-blue-900 mt-2">{total}</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                <span className="text-sm font-medium text-green-900">
                  Completed
                </span>
              </div>
              <p className="text-2xl font-bold text-green-900 mt-2">{completed}</p>
            </div>
            <div className="bg-yellow-50 rounded-lg p-4">
              <div className="flex items-center">
                <Clock className="h-5 w-5 text-yellow-600 mr-2" />
                <span className="text-sm font-medium text-yellow-900">
                  Partial
                </span>
              </div>
              <p className="text-2xl font-bold text-yellow-900 mt-2">{partial}</p>
            </div>
            <div className="bg-red-50 rounded-lg p-4">
              <div className="flex items-center">
                <XCircle className="h-5 w-5 text-red-600 mr-2" />
                <span className="text-sm font-medium text-red-900">
                  Failed
                </span>
              </div>
              <p className="text-2xl font-bold text-red-900 mt-2">{failed}</p>
            </div>
          </div>

          {/* Data Storage Location */}
          <div className="bg-slate-50 rounded-lg p-4 mb-6">
            <div className="flex items-center mb-2">
              <FolderOpen className="h-5 w-5 text-slate-600 mr-2" />
              <span className="text-sm font-medium text-slate-900">
                Data Storage Location
              </span>
            </div>
            <div className="bg-white rounded border p-3">
              <code className="text-sm text-slate-700">
                /audit/results/application-{applicationId}/
              </code>
            </div>
          </div>

          {/* Questions Table */}
          <div className="bg-white border border-slate-200 rounded-lg overflow-hidden mb-6">
            <div className="px-4 py-3 border-b border-slate-200 bg-slate-50">
              <h3 className="text-sm font-medium text-slate-900">
                Execution Results & Analysis
              </h3>
            </div>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Executive Summary</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Risk Level</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {(analyses as any[]).map((analysis: any) => {
                    const savedAnswer = (savedAnswers as any[]).find((answer: any) => answer.questionId === analysis.id);
                    const hasAnswer = !!savedAnswer;
                    const executiveSummary = hasAnswer ? 
                      (savedAnswer.findings?.analysis?.executiveSummary || 
                       savedAnswer.findings?.executiveSummary || 
                       "No executive summary available") : 
                      "No data collected";
                    
                    // Trim executive summary to 150 characters
                    const trimmedSummary = executiveSummary.length > 150 ? 
                      executiveSummary.substring(0, 150) + "..." : 
                      executiveSummary;

                    return (
                      <TableRow key={analysis.id}>
                        <TableCell className="font-medium">
                          {analysis.id}
                        </TableCell>
                        <TableCell className="max-w-md">
                          {hasAnswer ? (
                            <div className="space-y-1">
                              <p className="text-sm text-slate-700 leading-relaxed">
                                {trimmedSummary}
                              </p>
                              <div className="flex items-center space-x-2 text-xs text-slate-500">
                                <span>{savedAnswer.dataPoints} records analyzed</span>
                                <span>•</span>
                                <span>{savedAnswer.complianceStatus}</span>
                              </div>
                            </div>
                          ) : (
                            <span className="text-slate-400 text-sm">
                              No analysis available
                            </span>
                          )}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="text-xs">
                            {analysis.category}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {hasAnswer ? (
                            <Badge 
                              variant={
                                savedAnswer.riskLevel === 'Critical' ? 'destructive' :
                                savedAnswer.riskLevel === 'High' ? 'destructive' :
                                savedAnswer.riskLevel === 'Medium' ? 'secondary' : 'default'
                              }
                              className="text-xs"
                            >
                              {savedAnswer.riskLevel}
                            </Badge>
                          ) : (
                            <span className="text-slate-400 text-xs">N/A</span>
                          )}
                        </TableCell>
                        <TableCell>
                          {hasAnswer ? (
                            <Dialog>
                              <DialogTrigger asChild>
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  onClick={() => setSelectedAnswer(savedAnswer)}
                                >
                                  <Eye className="h-4 w-4 mr-1" />
                                  View Details
                                </Button>
                              </DialogTrigger>
                              <DialogContent className="max-w-4xl max-h-[80vh]">
                                <DialogHeader>
                                  <DialogTitle>Execution Details - {analysis.id}</DialogTitle>
                                </DialogHeader>
                                <ScrollArea className="max-h-[60vh] w-full">
                                  <div className="space-y-6 p-1">
                                    {/* Original Question */}
                                    <div>
                                      <h4 className="text-sm font-semibold text-slate-900 mb-2">Original Question</h4>
                                      <p className="text-sm text-slate-700 bg-slate-50 p-3 rounded">
                                        {analysis.originalQuestion}
                                      </p>
                                    </div>

                                    {/* Executive Summary */}
                                    <div>
                                      <h4 className="text-sm font-semibold text-slate-900 mb-2">Executive Summary</h4>
                                      <p className="text-sm text-slate-700 leading-relaxed">
                                        {executiveSummary}
                                      </p>
                                    </div>

                                    {/* Key Metrics */}
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                      <div className="bg-blue-50 p-3 rounded">
                                        <div className="text-xs text-blue-600 font-medium">Data Points</div>
                                        <div className="text-lg font-bold text-blue-900">{savedAnswer.dataPoints}</div>
                                      </div>
                                      <div className="bg-green-50 p-3 rounded">
                                        <div className="text-xs text-green-600 font-medium">Confidence</div>
                                        <div className="text-lg font-bold text-green-900">{savedAnswer.confidence}%</div>
                                      </div>
                                      <div className="bg-yellow-50 p-3 rounded">
                                        <div className="text-xs text-yellow-600 font-medium">Risk Level</div>
                                        <div className="text-lg font-bold text-yellow-900">{savedAnswer.riskLevel}</div>
                                      </div>
                                      <div className="bg-purple-50 p-3 rounded">
                                        <div className="text-xs text-purple-600 font-medium">Compliance</div>
                                        <div className="text-lg font-bold text-purple-900">{savedAnswer.complianceStatus}</div>
                                      </div>
                                    </div>

                                    {/* Findings */}
                                    {savedAnswer.findings?.findings && (
                                      <div>
                                        <h4 className="text-sm font-semibold text-slate-900 mb-2">Key Findings</h4>
                                        <ul className="space-y-2">
                                          {savedAnswer.findings.findings.map((finding: string, index: number) => (
                                            <li key={index} className="text-sm text-slate-700 flex">
                                              <span className="text-slate-400 mr-2">•</span>
                                              <span>{finding}</span>
                                            </li>
                                          ))}
                                        </ul>
                                      </div>
                                    )}

                                    {/* Tool Used */}
                                    <div>
                                      <h4 className="text-sm font-semibold text-slate-900 mb-2">Tool Used</h4>
                                      <div className="flex items-center space-x-2">
                                        <Badge variant="outline">{savedAnswer.toolUsed}</Badge>
                                        <span className="text-xs text-slate-500">
                                          Execution Time: {savedAnswer.executionTime}ms
                                        </span>
                                      </div>
                                    </div>
                                  </div>
                                </ScrollArea>
                              </DialogContent>
                            </Dialog>
                          ) : (
                            <span className="text-slate-400 text-sm">No actions</span>
                          )}
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          </div>

          {/* Generated Documents */}
          <div className="bg-slate-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-slate-900 mb-4">
              Generated Documents
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white rounded-lg p-4 flex items-center space-x-3">
                <FileText className="h-5 w-5 text-blue-600" />
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-slate-900">
                    Audit Report Summary
                  </h4>
                  <p className="text-xs text-slate-500">
                    {completed} questions completed • {total - completed} pending
                  </p>
                </div>
                <Button size="sm" variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
              </div>
              <div className="bg-white rounded-lg p-4 flex items-center space-x-3">
                <FileText className="h-5 w-5 text-green-600" />
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-slate-900">
                    Data Collection Log
                  </h4>
                  <p className="text-xs text-slate-500">
                    {(savedAnswers as any[]).reduce((sum: number, answer: any) => sum + (answer.dataPoints || 0), 0)} total records collected
                  </p>
                </div>
                <Button 
                  size="sm" 
                  variant="outline"
                  onClick={() => {
                    window.open(`http://localhost:8000/api/applications/${applicationId}/download-excel`, '_blank');
                  }}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
              </div>
            </div>
          </div>

          {/* Audit Status Management Section */}
          <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6 border border-green-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">
                  Audit Status Management
                </h3>
                <p className="text-sm text-slate-600 mb-4">
                  Current status: <strong>{(applicationData as any)?.status || 'In Progress'}</strong>
                </p>
                <p className="text-sm text-slate-600 mb-4">
                  {(applicationData as any)?.status === 'Completed' 
                    ? 'This audit has been marked as completed. You can reset it to "In Progress" if needed.'
                    : 'Mark this audit as completed to finalize all data collection and generate the final report.'
                  }
                </p>
                {(applicationData as any)?.status === 'Completed' && (
                  <Badge className="bg-green-100 text-green-800 mb-2">
                    Audit Completed
                  </Badge>
                )}
              </div>
              <div className="ml-6 flex gap-3">
                {(applicationData as any)?.status === 'Completed' ? (
                  <>
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button 
                          variant="outline"
                          disabled={completeAuditMutation.isPending}
                        >
                          <Clock className="h-4 w-4 mr-2" />
                          Reset to In Progress
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Reset Audit Status</AlertDialogTitle>
                          <AlertDialogDescription>
                            Are you sure you want to reset this audit status back to "In Progress"? 
                            This will allow further modifications to the audit data and results.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction 
                            onClick={() => resetAuditMutation.mutate()}
                            className="bg-orange-600 hover:bg-orange-700"
                          >
                            Yes, Reset Status
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                    <Button disabled variant="default" className="bg-green-600">
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Already Completed
                    </Button>
                  </>
                ) : (
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button 
                        size="lg" 
                        className="bg-green-600 hover:bg-green-700 text-white"
                        disabled={completeAuditMutation.isPending}
                      >
                        <CheckCircle className="h-4 w-4 mr-2" />
                        {completeAuditMutation.isPending ? 'Completing...' : 'Finish Audit'}
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Complete Audit</AlertDialogTitle>
                        <AlertDialogDescription>
                          Are you sure you want to mark this audit as completed? This action will:
                          <ul className="list-disc list-inside mt-2 space-y-1">
                            <li>Update the audit status to "Completed"</li>
                            <li>Finalize all data collection results</li>
                            <li>Generate the final audit report</li>
                            <li>Make the audit visible as completed in the dashboard</li>
                          </ul>
                          <br />
                          You can reset the status later if needed.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction 
                          onClick={() => completeAuditMutation.mutate()}
                          className="bg-green-600 hover:bg-green-700"
                        >
                          Yes, Complete Audit
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
