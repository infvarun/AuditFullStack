import { useQuery } from "@tanstack/react-query";
import { useEffect } from "react";
import { TrendingUp, CheckCircle, Clock, XCircle, CircleHelp, FileText, Download, FolderOpen } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../ui/table";

interface StepFiveProps {
  applicationId: number | null;
  setCanProceed: (canProceed: boolean) => void;
}

export default function StepFive({ applicationId, setCanProceed }: StepFiveProps) {
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

  // Step 5 is the final step, no next button needed
  // Always allow proceeding (validation removed)
  useEffect(() => {
    setCanProceed(true);
  }, [setCanProceed]);

  // Calculate statistics from saved answers
  const completed = savedAnswers.length;
  const partial = 0; // We don't have partial status in current implementation
  const failed = analyses.length - completed;
  const total = analyses.length;

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
                Audit Questions Status
              </h3>
            </div>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Question</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Document</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {analyses.map((analysis: any) => {
                    const savedAnswer = savedAnswers.find((answer: any) => answer.questionId === analysis.id);
                    const hasAnswer = !!savedAnswer;
                    return (
                      <TableRow key={analysis.id}>
                        <TableCell className="font-medium">
                          {analysis.id}
                        </TableCell>
                        <TableCell className="max-w-md truncate">
                          {analysis.originalQuestion}
                        </TableCell>
                        <TableCell>{analysis.category}</TableCell>
                        <TableCell>{getStatusBadge(hasAnswer)}</TableCell>
                        <TableCell>
                          {hasAnswer ? (
                            <div className="text-sm">
                              <div className="text-slate-600">
                                {savedAnswer.dataPoints} records
                              </div>
                              <div className="text-xs text-slate-500">
                                Risk: {savedAnswer.riskLevel} | {savedAnswer.complianceStatus}
                              </div>
                            </div>
                          ) : (
                            <span className="text-slate-400 text-sm">
                              No data collected
                            </span>
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
                    {savedAnswers.reduce((sum: number, answer: any) => sum + (answer.dataPoints || 0), 0)} total records collected
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
        </CardContent>
      </Card>
    </div>
  );
}
