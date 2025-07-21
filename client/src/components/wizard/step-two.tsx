import { useState, useCallback, useEffect } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { FileSpreadsheet, Upload, X, CheckCircle, List, Tags, Settings, Plus, Trash2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";
import { Separator } from "../ui/separator";
import { Badge } from "../ui/badge";
import { apiRequest } from "../../lib/queryClient";
import { useToast } from "../../hooks/use-toast";

interface StepTwoProps {
  applicationId: number | null;
  onNext: () => void;
  setCanProceed: (canProceed: boolean) => void;
}

interface ColumnMapping {
  questionNumber: string;
  process: string;
  subProcess: string;
  question: string;
}

interface FileUploadState {
  file: File | null;
  columns: string[];
  sampleData: any[];
  columnMappings: ColumnMapping;
  isProcessing: boolean;
}

export default function StepTwo({ applicationId, onNext, setCanProceed }: StepTwoProps) {
  const [primaryFile, setPrimaryFile] = useState<FileUploadState>({
    file: null,
    columns: [],
    sampleData: [],
    columnMappings: {
      questionNumber: '',
      process: '',
      subProcess: '',
      question: ''
    },
    isProcessing: false
  });
  
  const [followupFiles, setFollowupFiles] = useState<FileUploadState[]>([]);
  const [showColumnMapping, setShowColumnMapping] = useState(false);
  const [processingFile, setProcessingFile] = useState<'primary' | 'followup' | null>(null);
  const [currentFileIndex, setCurrentFileIndex] = useState<number | null>(null);

  const { toast } = useToast();

  const { data: dataRequests, isLoading, refetch } = useQuery({
    queryKey: ["/api/data-requests/application", applicationId],
    enabled: !!applicationId,
  });

  // Get application data to check follow-up questions setting
  const { data: applicationData } = useQuery({
    queryKey: [`/api/applications/${applicationId}`],
    enabled: !!applicationId,
  });

  // Check if we have processed files to allow proceeding
  useEffect(() => {
    const hasPrimaryFile = Array.isArray(dataRequests) && dataRequests.some((req: any) => req.fileType === 'primary');
    setCanProceed(!!hasPrimaryFile);
  }, [dataRequests, setCanProceed]);

  // Initialize follow-up files when enabled in settings
  useEffect(() => {
    console.log("Follow-up effect triggered:", { 
      enableFollowupQuestions: applicationData?.enableFollowupQuestions, 
      followupFilesLength: followupFiles.length,
      applicationData 
    });
    
    if (applicationData?.enableFollowupQuestions && followupFiles.length === 0) {
      console.log("Adding initial follow-up file slot");
      setFollowupFiles([{
        file: null,
        columns: [],
        sampleData: [],
        columnMappings: {
          questionNumber: '',
          process: '',
          subProcess: '',
          question: ''
        },
        isProcessing: false
      }]);
    } else if (applicationData?.enableFollowupQuestions === false) {
      console.log("Clearing follow-up files");
      setFollowupFiles([]);
    }
  }, [applicationData?.enableFollowupQuestions]);

  // Get columns from uploaded Excel file
  const getColumnsMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      
      const response = await apiRequest("POST", "/api/excel/get-columns", formData);
      return response.json();
    },
    onSuccess: (data, file) => {
      if (processingFile === 'primary') {
        setPrimaryFile(prev => ({
          ...prev,
          columns: data.columns,
          sampleData: data.sampleData || data.sample_data || [],
          file: file
        }));
      } else if (processingFile === 'followup' && currentFileIndex !== null) {
        setFollowupFiles(prev => {
          const newFiles = [...prev];
          newFiles[currentFileIndex] = {
            ...newFiles[currentFileIndex],
            columns: data.columns,
            sampleData: data.sampleData || data.sample_data || [],
            file: file
          };
          return newFiles;
        });
      }
      setShowColumnMapping(true);
    },
    onError: (error) => {
      toast({
        title: "Failed to analyze file",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  // Process Excel file with column mappings
  const processExcelMutation = useMutation({
    mutationFn: async ({ file, columnMappings, fileType }: { file: File, columnMappings: ColumnMapping, fileType: string }) => {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("applicationId", applicationId!.toString());
      formData.append("fileType", fileType);
      formData.append("columnMappings", JSON.stringify(columnMappings));
      
      const response = await apiRequest("POST", "/api/excel/process", formData);
      return response.json();
    },
    onSuccess: (data) => {
      toast({
        title: "File processed successfully",
        description: `${data.totalQuestions} questions processed from ${data.fileName}`,
      });
      refetch();
      setShowColumnMapping(false);
      setProcessingFile(null);
      setCurrentFileIndex(null);
    },
    onError: (error) => {
      toast({
        title: "Processing failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  // Helper functions
  const addFollowupFile = () => {
    setFollowupFiles(prev => [...prev, {
      file: null,
      columns: [],
      sampleData: [],
      columnMappings: {
        questionNumber: '',
        process: '',
        subProcess: '',
        question: ''
      },
      isProcessing: false
    }]);
  };

  const removeFollowupFile = (index: number) => {
    setFollowupFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>, fileType: 'primary' | 'followup', index?: number) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setProcessingFile(fileType);
    if (fileType === 'followup' && index !== undefined) {
      setCurrentFileIndex(index);
    }
    
    getColumnsMutation.mutate(file);
  };

  const updateColumnMapping = (field: keyof ColumnMapping, value: string, fileType: 'primary' | 'followup', index?: number) => {
    if (fileType === 'primary') {
      setPrimaryFile(prev => ({
        ...prev,
        columnMappings: {
          ...prev.columnMappings,
          [field]: value
        }
      }));
    } else if (fileType === 'followup' && index !== undefined) {
      setFollowupFiles(prev => {
        const newFiles = [...prev];
        newFiles[index] = {
          ...newFiles[index],
          columnMappings: {
            ...newFiles[index].columnMappings,
            [field]: value
          }
        };
        return newFiles;
      });
    }
  };

  const handleProcessFile = (fileType: 'primary' | 'followup', index?: number) => {
    let file, columnMappings;
    
    if (fileType === 'primary') {
      file = primaryFile.file;
      columnMappings = primaryFile.columnMappings;
    } else if (fileType === 'followup' && index !== undefined) {
      file = followupFiles[index].file;
      columnMappings = followupFiles[index].columnMappings;
    }

    if (!file) {
      toast({
        title: "No file selected",
        description: "Please select a file first",
        variant: "destructive",
      });
      return;
    }

    processExcelMutation.mutate({
      file,
      columnMappings,
      fileType
    });
  };

  // Column mapping component
  const ColumnMappingForm = ({ fileState, fileType, index }: { fileState: FileUploadState, fileType: 'primary' | 'followup', index?: number }) => {
    const isValid = fileState.columnMappings.questionNumber && 
                   fileState.columnMappings.process && 
                   fileState.columnMappings.subProcess && 
                   fileState.columnMappings.question;

    return (
      <Card className="mt-4">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Settings className="h-5 w-5" />
            <span>Column Mapping</span>
          </CardTitle>
          <p className="text-sm text-slate-600">
            Map the Excel columns to the required fields
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="questionNumber">Question Number Column</Label>
              <Select 
                value={fileState.columnMappings.questionNumber} 
                onValueChange={(value) => updateColumnMapping('questionNumber', value, fileType, index)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select column" />
                </SelectTrigger>
                <SelectContent>
                  {fileState.columns.map(col => (
                    <SelectItem key={col} value={col}>{col}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="process">Process (Category) Column</Label>
              <Select 
                value={fileState.columnMappings.process} 
                onValueChange={(value) => updateColumnMapping('process', value, fileType, index)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select column" />
                </SelectTrigger>
                <SelectContent>
                  {fileState.columns.map(col => (
                    <SelectItem key={col} value={col}>{col}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="subProcess">Sub-Process (Sub-Category) Column</Label>
              <Select 
                value={fileState.columnMappings.subProcess} 
                onValueChange={(value) => updateColumnMapping('subProcess', value, fileType, index)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select column" />
                </SelectTrigger>
                <SelectContent>
                  {fileState.columns.map(col => (
                    <SelectItem key={col} value={col}>{col}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="question">Question Column</Label>
              <Select 
                value={fileState.columnMappings.question} 
                onValueChange={(value) => updateColumnMapping('question', value, fileType, index)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select column" />
                </SelectTrigger>
                <SelectContent>
                  {fileState.columns.map(col => (
                    <SelectItem key={col} value={col}>{col}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Sample Data Preview */}
          {fileState.sampleData.length > 0 && (
            <div className="mt-4">
              <Label>Sample Data Preview</Label>
              <div className="mt-2 overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      {fileState.columns.map(col => (
                        <th key={col} className="text-left p-2 font-medium">{col}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {fileState.sampleData.slice(0, 3).map((row, index) => (
                      <tr key={index} className="border-b">
                        {fileState.columns.map(col => (
                          <td key={col} className="p-2 text-slate-600">{row[col]}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <div className="flex justify-end space-x-2">
            <Button 
              variant="outline" 
              onClick={() => setShowColumnMapping(false)}
            >
              Cancel
            </Button>
            <Button 
              onClick={() => handleProcessFile(fileType, index)}
              disabled={!isValid || processExcelMutation.isPending}
            >
              {processExcelMutation.isPending ? "Processing..." : "Process File"}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  };

  // Get processed files for display
  const processedPrimaryFiles = Array.isArray(dataRequests) ? dataRequests.filter((req: any) => req.fileType === 'primary') : [];
  const processedFollowupFiles = Array.isArray(dataRequests) ? dataRequests.filter((req: any) => req.fileType === 'followup') : [];

  // Processed files section component
  const ProcessedFilesSection = () => (
    <>
      {/* Primary Data Request Files */}
      {processedPrimaryFiles.length > 0 && (
        <Card className="card-modern">
          <CardHeader>
            <CardTitle className="flex items-center space-x-3">
              <FileSpreadsheet className="h-5 w-5 text-green-600" />
              <span className="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                Primary Data Request Files
              </span>
            </CardTitle>
          </CardHeader>
          
          <CardContent>
            {processedPrimaryFiles.map((dataRequest: any, index: number) => (
              <div key={index} className="mb-6 last:mb-0">
                <div className="bg-slate-50 rounded-lg p-4">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <FileSpreadsheet className="h-8 w-8 text-green-600" />
                    </div>
                    <div className="flex-1">
                      <h4 className="text-sm font-medium text-slate-900">
                        {dataRequest.fileName}
                      </h4>
                      <p className="text-xs text-slate-500">
                        {(dataRequest.fileSize / 1024 / 1024).toFixed(1)} MB • {dataRequest.totalQuestions} questions • {dataRequest.categories?.length || 0} categories
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="secondary" className="bg-green-100 text-green-800">
                        Processed
                      </Badge>
                    </div>
                  </div>
                  
                  {/* Summary Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                    <div className="bg-blue-50 rounded-lg p-4">
                      <div className="flex items-center space-x-3">
                        <List className="h-5 w-5 text-blue-600" />
                        <div>
                          <p className="text-sm font-medium text-slate-900">Total Questions</p>
                          <p className="text-2xl font-bold text-blue-600">{dataRequest.totalQuestions}</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-purple-50 rounded-lg p-4">
                      <div className="flex items-center space-x-3">
                        <Tags className="h-5 w-5 text-purple-600" />
                        <div>
                          <p className="text-sm font-medium text-slate-900">Categories</p>
                          <p className="text-2xl font-bold text-purple-600">{dataRequest.categories?.length || 0}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Follow-up Question Files - Only show if enabled in settings */}
      {applicationData?.enableFollowupQuestions && processedFollowupFiles.length > 0 && (
        <Card className="card-modern">
          <CardHeader>
            <CardTitle className="flex items-center space-x-3">
              <FileSpreadsheet className="h-5 w-5 text-purple-600" />
              <span className="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                Follow-up Question Files
              </span>
            </CardTitle>
          </CardHeader>
          
          <CardContent>
            {processedFollowupFiles.map((dataRequest: any, index: number) => (
              <div key={index} className="mb-6 last:mb-0">
                <div className="bg-slate-50 rounded-lg p-4">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <FileSpreadsheet className="h-8 w-8 text-purple-600" />
                    </div>
                    <div className="flex-1">
                      <h4 className="text-sm font-medium text-slate-900">
                        {dataRequest.fileName}
                      </h4>
                      <p className="text-xs text-slate-500">
                        {(dataRequest.fileSize / 1024 / 1024).toFixed(1)} MB • {dataRequest.totalQuestions} questions • {dataRequest.categories?.length || 0} categories
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="secondary" className="bg-purple-100 text-purple-800">
                        Follow-up
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </>
  );

  return (
    <div className="space-y-8">
      {/* Show processed files first */}
      <ProcessedFilesSection />

      {/* Primary Data Request File Upload - Only show if no processed primary files */}
      {processedPrimaryFiles.length === 0 && (
        <Card className="card-modern">
          <CardHeader>
            <CardTitle className="flex items-center space-x-3">
              <FileSpreadsheet className="h-5 w-5 text-purple-600" />
              <span className="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                Primary Data Request File Upload
              </span>
            </CardTitle>
            <p className="text-sm text-slate-600">
              Upload the main Excel file containing audit questions and requirements
            </p>
          </CardHeader>
          
          <CardContent>
            {/* File Upload Zone */}
            <div className="border-2 border-dashed border-purple-300 rounded-lg p-8 text-center hover:border-purple-500 hover:bg-purple-50/50 transition-all duration-300">
              <Upload className="mx-auto h-12 w-12 text-purple-400 mb-4" />
              <h3 className="text-lg font-medium text-slate-900 mb-2">
                Drop your Excel file here
              </h3>
              <p className="text-sm text-slate-500 mb-4">
                or click to browse files
              </p>
              <div className="relative">
                <input
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={(e) => handleFileSelect(e, 'primary')}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                <Button variant="outline" className="btn-gradient-outline">Select File</Button>
              </div>
              <p className="text-xs text-slate-400 mt-4">
                Supported formats: .xlsx, .xls (Max size: 10MB)
              </p>
            </div>

            {/* Column Mapping for Primary File */}
            {showColumnMapping && processingFile === 'primary' && (
              <ColumnMappingForm fileState={primaryFile} fileType="primary" />
            )}
          </CardContent>
        </Card>
      )}

      {/* Follow-up Question File Upload - Always show if enabled in settings */}
      {applicationData?.enableFollowupQuestions && (
        <Card className="card-modern">
          <CardHeader>
            <CardTitle className="flex items-center space-x-3">
              <FileSpreadsheet className="h-5 w-5 text-green-600" />
              <span className="bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
                Follow-up Question File Upload
              </span>
            </CardTitle>
            <p className="text-sm text-slate-600">
              Upload additional Excel files for follow-up questions (optional)
            </p>
          </CardHeader>
        
        <CardContent>
          {followupFiles.map((fileState, index) => (
            <div key={index} className="mb-6 last:mb-0 border border-slate-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-sm font-medium text-slate-900">
                  Follow-up File #{index + 1}
                </h4>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => removeFollowupFile(index)}
                  className="text-red-500 hover:text-red-700"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>

              <div className="border-2 border-dashed border-green-300 rounded-lg p-6 text-center hover:border-green-500 hover:bg-green-50/50 transition-all duration-300">
                <Upload className="mx-auto h-8 w-8 text-green-400 mb-3" />
                <p className="text-sm text-slate-500 mb-3">
                  Drop your Excel file here or click to browse
                </p>
                <div className="relative">
                  <input
                    type="file"
                    accept=".xlsx,.xls"
                    onChange={(e) => handleFileSelect(e, 'followup', index)}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                  <Button variant="outline" size="sm">Select File</Button>
                </div>
              </div>

              {/* Column Mapping for Follow-up File */}
              {showColumnMapping && processingFile === 'followup' && currentFileIndex === index && (
                <ColumnMappingForm fileState={fileState} fileType="followup" index={index} />
              )}
            </div>
          ))}

          <div className="flex justify-center">
            <Button
              onClick={addFollowupFile}
              variant="outline"
              className="flex items-center space-x-2"
            >
              <Plus className="h-4 w-4" />
              <span>Add Follow-up File</span>
            </Button>
          </div>
        </CardContent>
        </Card>
      )}
    </div>
  );
}