import { useState, useEffect, useRef } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useLocation } from "wouter";
import { 
  ArrowLeft, 
  Send, 
  Bot, 
  User, 
  FileText,
  Brain,
  Settings,
  MessageCircle,
  Upload,
  Clock,
  CheckCircle
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Separator } from "../components/ui/separator";
import { ScrollArea } from "../components/ui/scroll-area";
import type { Application, ContextDocument } from "@shared/schema";
import { apiRequest, queryClient } from "../lib/queryClient";
import { useToast } from "../hooks/use-toast";

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  thinking?: string[];
}

interface ThinkingStep {
  step: string;
  status: 'pending' | 'loading' | 'completed';
}

export default function VeritasGPT() {
  const [, setLocation] = useLocation();
  const [selectedAuditId, setSelectedAuditId] = useState<string>("");
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [thinkingSteps, setThinkingSteps] = useState<ThinkingStep[]>([]);
  const [conversationId, setConversationId] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  // Fetch applications for CI selection
  const { data: applications = [] } = useQuery<Application[]>({
    queryKey: ["/api/applications"],
  });

  // Get selected audit info
  const selectedAudit = applications.find(app => app.id.toString() === selectedAuditId);
  
  // Fetch context documents for selected audit's CI
  const { data: contextDocuments = [] } = useQuery<ContextDocument[]>({
    queryKey: ["/api/context-documents", selectedAudit?.ciId],
    enabled: !!selectedAudit?.ciId,
  });

  // Fetch data collection forms for selected audit
  const { data: dataRequests = [] } = useQuery<any[]>({
    queryKey: ["/api/data-requests", selectedAuditId],
    enabled: !!selectedAuditId,
  });

  // Chat mutation
  const chatMutation = useMutation({
    mutationFn: async ({ message, auditId }: { message: string; auditId: string }) => {
      const audit = applications.find(app => app.id.toString() === auditId);
      if (!audit) throw new Error("Audit not found");
      
      const response = await apiRequest("POST", "/api/veritas-gpt/chat", {
        message,
        ciId: audit.ciId,
        auditId: auditId,
        auditName: audit.auditName,
        conversationId: conversationId || undefined,
      });
      return response.json();
    },
    onMutate: ({ message }) => {
      // Add user message immediately
      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content: message,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, userMessage]);
      setMessage("");
      setIsLoading(true);
      
      // Initialize thinking steps
      setThinkingSteps([
        { step: "Reading Support Plan", status: 'loading' },
        { step: "Analyzing Design Diagram", status: 'pending' },
        { step: "Processing Additional Supplements", status: 'pending' },
        { step: "Searching audit context", status: 'pending' },
        { step: "Generating response", status: 'pending' },
      ]);
    },
    onSuccess: (data) => {
      setConversationId(data.conversationId);
      
      // Simulate thinking process
      let currentStep = 0;
      const interval = setInterval(() => {
        setThinkingSteps(prev => {
          const newSteps = [...prev];
          if (currentStep > 0) {
            newSteps[currentStep - 1].status = 'completed';
          }
          if (currentStep < newSteps.length) {
            newSteps[currentStep].status = 'loading';
          }
          return newSteps;
        });
        
        currentStep++;
        if (currentStep > thinkingSteps.length) {
          clearInterval(interval);
          
          // Add assistant response
          const assistantMessage: Message = {
            id: Date.now().toString() + '_assistant',
            role: 'assistant',
            content: data.response,
            timestamp: new Date(),
            thinking: data.contextUsed || [],
          };
          
          setMessages(prev => [...prev, assistantMessage]);
          setIsLoading(false);
          setThinkingSteps([]);
        }
      }, 800);
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
      setIsLoading(false);
      setThinkingSteps([]);
    },
  });

  const handleSendMessage = () => {
    if (!message.trim() || !selectedAuditId || isLoading) return;
    
    chatMutation.mutate({
      message: message.trim(),
      auditId: selectedAuditId,
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, thinkingSteps]);

  const getDocumentTypeLabel = (type: string) => {
    switch (type) {
      case 'support_plan': return 'Support Plan';
      case 'design_diagram': return 'Design Diagram';
      case 'additional_supplements': return 'Additional Supplements';
      default: return 'Other Document';
    }
  };

  const getDocumentTypeIcon = (type: string) => {
    switch (type) {
      case 'support_plan': return <FileText className="h-4 w-4 text-blue-500" />;
      case 'design_diagram': return <Settings className="h-4 w-4 text-green-500" />;
      case 'additional_supplements': return <Upload className="h-4 w-4 text-purple-500" />;
      default: return <FileText className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-purple-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                onClick={() => setLocation("/")}
                className="text-slate-600 hover:text-slate-900"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
              <Separator orientation="vertical" className="h-6" />
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg flex items-center justify-center">
                  <Brain className="h-5 w-5 text-white" />
                </div>
                <h1 className="text-xl font-bold text-slate-900">Veritas GPT</h1>
                <Badge variant="secondary" className="bg-purple-100 text-purple-700">
                  Context-Aware AI
                </Badge>
              </div>
            </div>
            
            <Button
              variant="outline"
              onClick={() => setLocation("/settings")}
              className="text-slate-600 hover:text-slate-900"
            >
              <Settings className="h-4 w-4 mr-2" />
              Manage Context
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          
          {/* Sidebar - Context & Controls */}
          <div className="lg:col-span-1 space-y-6">
            {/* Audit Selection */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <MessageCircle className="h-5 w-5 mr-2 text-purple-600" />
                  Select Audit
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Select value={selectedAuditId} onValueChange={setSelectedAuditId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose an audit to chat about..." />
                  </SelectTrigger>
                  <SelectContent>
                    {applications.map((app) => (
                      <SelectItem key={app.id} value={app.id.toString()}>
                        <div className="flex flex-col">
                          <span className="font-medium">{app.auditName}</span>
                          <span className="text-xs text-slate-500">CI: {app.ciId}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>

            {/* Audit Information */}
            {selectedAuditId && selectedAudit && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center">
                    <FileText className="h-5 w-5 mr-2 text-blue-600" />
                    Audit Context
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <p className="text-sm font-medium text-blue-900">{selectedAudit.auditName}</p>
                    <p className="text-xs text-blue-700">CI: {selectedAudit.ciId}</p>
                    <p className="text-xs text-blue-600">Status: {selectedAudit.status}</p>
                  </div>
                  
                  {/* Context Documents */}
                  <div>
                    <h4 className="text-sm font-medium mb-2">Context Documents</h4>
                    {contextDocuments.length > 0 ? (
                      <div className="space-y-2">
                        {contextDocuments.map((doc) => (
                          <div key={doc.id} className="flex items-center space-x-2 p-2 bg-slate-50 rounded">
                            {getDocumentTypeIcon(doc.documentType)}
                            <div className="flex-1 min-w-0">
                              <p className="text-xs font-medium truncate">{getDocumentTypeLabel(doc.documentType)}</p>
                              <p className="text-xs text-slate-500 truncate">{doc.fileName}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-3">
                        <p className="text-xs text-slate-500 mb-2">No context documents</p>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setLocation("/settings")}
                        >
                          Upload Context
                        </Button>
                      </div>
                    )}
                  </div>

                  {/* Data Collection Forms */}
                  <div>
                    <h4 className="text-sm font-medium mb-2">Data Collection</h4>
                    {dataRequests.length > 0 ? (
                      <div className="space-y-2">
                        {dataRequests.map((req: any, idx: number) => (
                          <div key={idx} className="p-2 bg-green-50 rounded">
                            <p className="text-xs font-medium text-green-900">
                              {req.fileType === 'primary' ? 'Primary Questions' : 'Follow-up Questions'}
                            </p>
                            <p className="text-xs text-green-700">{req.totalQuestions} questions</p>
                            <p className="text-xs text-green-600 truncate">{req.fileName}</p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-slate-500">No data collection forms</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Main Chat Area */}
          <div className="lg:col-span-3">
            <Card className="h-[calc(100vh-12rem)]">
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center">
                  <Bot className="h-5 w-5 mr-2 text-purple-600" />
                  Audit Context Chat
                </CardTitle>
              </CardHeader>
              
              <CardContent className="flex flex-col h-full">
                {/* Messages Area */}
                <ScrollArea className="flex-1 pr-4 mb-4">
                  <div className="space-y-4">
                    {!selectedAuditId ? (
                      <div className="text-center py-12">
                        <Bot className="h-16 w-16 text-slate-300 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-slate-900 mb-2">
                          Select an Audit to Start
                        </h3>
                        <p className="text-slate-500">
                          Choose an audit from the sidebar to begin your context-aware conversation
                        </p>
                      </div>
                    ) : messages.length === 0 ? (
                      <div className="text-center py-12">
                        <Brain className="h-16 w-16 text-purple-300 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-slate-900 mb-2">
                          Veritas GPT Ready
                        </h3>
                        <p className="text-slate-500">
                          Ask questions about your audit data and context documents
                        </p>
                      </div>
                    ) : (
                      <>
                        {messages.map((msg) => (
                          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[80%] rounded-lg p-4 ${
                              msg.role === 'user'
                                ? 'bg-purple-600 text-white'
                                : 'bg-slate-100 text-slate-900'
                            }`}>
                              <div className="flex items-start space-x-2">
                                {msg.role === 'assistant' && (
                                  <Bot className="h-5 w-5 text-purple-600 mt-0.5 flex-shrink-0" />
                                )}
                                <div className="flex-1">
                                  <p className="text-sm">{msg.content}</p>
                                  {msg.thinking && msg.thinking.length > 0 && (
                                    <div className="mt-3 pt-3 border-t border-slate-200">
                                      <p className="text-xs text-slate-600 mb-2">Context used:</p>
                                      <div className="flex flex-wrap gap-1">
                                        {msg.thinking.map((context, idx) => (
                                          <Badge key={idx} variant="secondary" className="text-xs">
                                            {context}
                                          </Badge>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                </div>
                                {msg.role === 'user' && (
                                  <User className="h-5 w-5 text-white mt-0.5 flex-shrink-0" />
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                        
                        {/* Thinking Steps */}
                        {isLoading && thinkingSteps.length > 0 && (
                          <div className="flex justify-start">
                            <div className="max-w-[80%] rounded-lg p-4 bg-slate-100">
                              <div className="flex items-start space-x-2">
                                <Bot className="h-5 w-5 text-purple-600 mt-0.5 flex-shrink-0" />
                                <div className="flex-1">
                                  <p className="text-sm text-slate-700 mb-3">Thinking...</p>
                                  <div className="space-y-2">
                                    {thinkingSteps.map((step, idx) => (
                                      <div key={idx} className="flex items-center space-x-2">
                                        {step.status === 'completed' ? (
                                          <CheckCircle className="h-4 w-4 text-green-500" />
                                        ) : step.status === 'loading' ? (
                                          <Clock className="h-4 w-4 text-blue-500 animate-spin" />
                                        ) : (
                                          <div className="h-4 w-4 rounded-full border-2 border-slate-300" />
                                        )}
                                        <span className={`text-xs ${
                                          step.status === 'completed' 
                                            ? 'text-green-700' 
                                            : step.status === 'loading'
                                            ? 'text-blue-700'
                                            : 'text-slate-500'
                                        }`}>
                                          {step.step}
                                        </span>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        )}
                      </>
                    )}
                    <div ref={messagesEndRef} />
                  </div>
                </ScrollArea>

                {/* Input Area */}
                {selectedAuditId && (
                  <div className="border-t pt-4">
                    <div className="flex items-center space-x-2 bg-slate-50 rounded-lg p-2 border border-slate-200 focus-within:border-purple-500 focus-within:ring-2 focus-within:ring-purple-500/20">
                      <textarea
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask about your audit context..."
                        disabled={isLoading}
                        rows={1}
                        className="flex-1 resize-none bg-transparent border-none outline-none text-sm placeholder:text-slate-500 disabled:cursor-not-allowed disabled:opacity-50 min-h-[40px] max-h-[120px] py-2 px-2"
                        style={{ 
                          lineHeight: '1.5',
                          overflowY: message.split('\n').length > 2 ? 'auto' : 'hidden'
                        }}
                        onInput={(e) => {
                          const target = e.target as HTMLTextAreaElement;
                          target.style.height = 'auto';
                          target.style.height = Math.min(target.scrollHeight, 120) + 'px';
                        }}
                      />
                      <Button
                        onClick={handleSendMessage}
                        disabled={!message.trim() || isLoading}
                        className="bg-purple-600 hover:bg-purple-700 text-white h-8 w-8 rounded-md flex-shrink-0 p-0"
                        size="sm"
                      >
                        <Send className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}