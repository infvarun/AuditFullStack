import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useLocation } from "wouter";
import { ArrowLeft, Database, Settings as SettingsIcon, FolderOpen, Search, Plus, Edit2, Trash2, Activity, CheckCircle, XCircle, AlertCircle, RefreshCw } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Separator } from "../components/ui/separator";
import { apiRequest, queryClient } from "../lib/queryClient";
import { useToast } from "../hooks/use-toast";

interface ConnectorConfig {
  type: string;
  name: string;
  icon: React.ReactNode;
  fields: Array<{
    key: string;
    label: string;
    type: string;
    placeholder: string;
    required?: boolean;
  }>;
}

const connectorConfigs: ConnectorConfig[] = [
  {
    type: "SQL Server DB",
    name: "SQL Server DB",
    icon: <Database className="h-5 w-5 text-blue-600" />,
    fields: [
      { key: "server", label: "Server Address", type: "text", placeholder: "e.g., sql-server.company.com", required: true },
      { key: "port", label: "Port", type: "number", placeholder: "1433", required: true },
      { key: "database", label: "Database Name", type: "text", placeholder: "Database Name", required: true },
      { key: "username", label: "Username", type: "text", placeholder: "Username", required: false },
      { key: "password", label: "Password", type: "password", placeholder: "Password", required: false },
    ],
  },
  {
    type: "Oracle DB",
    name: "Oracle DB", 
    icon: <Database className="h-5 w-5 text-orange-600" />,
    fields: [
      { key: "server", label: "Server Address", type: "text", placeholder: "e.g., oracle-server.company.com", required: true },
      { key: "port", label: "Port", type: "number", placeholder: "1521", required: true },
      { key: "service_name", label: "Service Name", type: "text", placeholder: "ORCL", required: true },
      { key: "username", label: "Username", type: "text", placeholder: "Username", required: false },
      { key: "password", label: "Password", type: "password", placeholder: "Password", required: false },
    ],
  },
  {
    type: "Gnosis Document Repository",
    name: "Gnosis Document Repository",
    icon: <FolderOpen className="h-5 w-5 text-purple-600" />,
    fields: [
      { key: "server", label: "Server Address", type: "text", placeholder: "docs.company.com", required: true },
      { key: "api_endpoint", label: "API Endpoint", type: "text", placeholder: "/api/v2/documents", required: true },
      { key: "repository", label: "Repository", type: "text", placeholder: "security-policies", required: true },
      { key: "api_key", label: "API Key", type: "password", placeholder: "API Key", required: false },
    ],
  },
  {
    type: "Jira",
    name: "Jira",
    icon: <SettingsIcon className="h-5 w-5 text-blue-500" />,
    fields: [
      { key: "server", label: "Server Address", type: "text", placeholder: "company.atlassian.net", required: true },
      { key: "project_key", label: "Project Key", type: "text", placeholder: "SEC", required: true },
      { key: "api_version", label: "API Version", type: "text", placeholder: "3", required: true },
      { key: "username", label: "Username", type: "text", placeholder: "Username", required: false },
      { key: "api_token", label: "API Token", type: "password", placeholder: "API Token", required: false },
    ],
  },
  {
    type: "QTest",
    name: "QTest",
    icon: <CheckCircle className="h-5 w-5 text-green-600" />,
    fields: [
      { key: "server", label: "Server Address", type: "text", placeholder: "company.qtestnet.com", required: true },
      { key: "project_id", label: "Project ID", type: "text", placeholder: "12345", required: true },
      { key: "api_version", label: "API Version", type: "text", placeholder: "v3", required: true },
      { key: "api_token", label: "API Token", type: "password", placeholder: "API Token", required: false },
    ],
  },
  {
    type: "ServiceNow",
    name: "ServiceNow",
    icon: <SettingsIcon className="h-5 w-5 text-red-600" />,
    fields: [
      { key: "instance", label: "Instance", type: "text", placeholder: "company.service-now.com", required: true },
      { key: "endpoint", label: "API Endpoint", type: "text", placeholder: "api/now/table/incident", required: true },
      { key: "version", label: "API Version", type: "text", placeholder: "v1", required: true },
      { key: "username", label: "Username", type: "text", placeholder: "Username", required: false },
      { key: "password", label: "Password", type: "password", placeholder: "Password", required: false },
    ],
  },
];

export default function Settings() {
  const [, navigate] = useLocation();
  const { toast } = useToast();
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCi, setSelectedCi] = useState("");
  const [editingConnector, setEditingConnector] = useState<any>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [selectedConnectorType, setSelectedConnectorType] = useState("");
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [activeMenuItem, setActiveMenuItem] = useState("connectors");

  // Get all unique CI IDs
  const { data: applications } = useQuery({
    queryKey: ["/api/applications"],
  });

  // Get connectors for selected CI
  const { data: connectors, refetch: refetchConnectors } = useQuery({
    queryKey: ["/api/connectors/ci", selectedCi],
    enabled: !!selectedCi,
  });

  // Database health check query
  const { data: dbHealth, isLoading: dbHealthLoading, refetch: refetchDbHealth } = useQuery({
    queryKey: ["/api/database/health"],
    queryFn: async () => {
      const response = await apiRequest("GET", "/api/database/health");
      const data = await response.json();
      return { ...data, httpStatus: response.status };
    },
    enabled: activeMenuItem === "database",
    refetchOnWindowFocus: false,
  });

  // Create/Update connector mutation
  const saveConnectorMutation = useMutation({
    mutationFn: async (data: any) => {
      const method = editingConnector ? "PUT" : "POST";
      const url = editingConnector ? `/api/connectors/${editingConnector.id}` : "/api/connectors";
      const response = await apiRequest(method, url, data);
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: editingConnector ? "Connector updated" : "Connector created",
        description: "Configuration saved successfully.",
      });
      setIsCreateDialogOpen(false);
      setEditingConnector(null);
      setFormData({});
      refetchConnectors();
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  // Delete connector mutation
  const deleteConnectorMutation = useMutation({
    mutationFn: async (id: number) => {
      const response = await apiRequest("DELETE", `/api/connectors/${id}`);
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Connector deleted",
        description: "Configuration removed successfully.",
      });
      refetchConnectors();
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  // Test connector mutation
  const testConnectorMutation = useMutation({
    mutationFn: async (id: number) => {
      const response = await apiRequest("POST", `/api/connectors/${id}/test`);
      return response.json();
    },
    onSuccess: (data: any) => {
      toast({
        title: data.success ? "Connection successful" : "Connection failed",
        description: data.message + (data.testDuration ? ` (${data.testDuration.toFixed(2)}s)` : ""),
        variant: data.success ? "default" : "destructive",
      });
      refetchConnectors();
    },
    onError: (error: any) => {
      toast({
        title: "Connection test failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  // Get unique CI IDs from applications
  const uniqueCiIds = (applications as any[])?.map((app: any) => app.ciId).filter((value: string, index: number, self: string[]) => self.indexOf(value) === index) || [];
  const filteredCiIds = uniqueCiIds.filter((ciId: string) => ciId.toLowerCase().includes(searchTerm.toLowerCase()));

  const handleCreateConnector = () => {
    setEditingConnector(null);
    setSelectedConnectorType("");
    setFormData({});
    setIsCreateDialogOpen(true);
  };

  const handleEditConnector = (connector: any) => {
    setEditingConnector(connector);
    setSelectedConnectorType(connector.connectorType);
    setFormData(connector.configuration || {});
    setIsCreateDialogOpen(true);
  };

  const handleSaveConnector = () => {
    if (!selectedCi || !selectedConnectorType) return;

    const connectorData = {
      ciId: selectedCi,
      connectorType: selectedConnectorType,
      configuration: formData,
    };

    saveConnectorMutation.mutate(connectorData);
  };

  const selectedConnectorConfig = connectorConfigs.find(c => c.type === selectedConnectorType);

  const renderConnectorsContent = () => (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* CI Selection */}
      <Card className="card-modern">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Search className="h-5 w-5" />
            <span>Select CI</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <Label htmlFor="search">Search CI</Label>
              <Input
                id="search"
                placeholder="Search CI ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            
            <div className="max-h-96 overflow-y-auto space-y-2">
              {filteredCiIds.map((ciId: string) => (
                <div
                  key={ciId}
                  className={`p-3 rounded-lg border cursor-pointer transition-all ${
                    selectedCi === ciId
                      ? "border-blue-500 bg-blue-50 text-blue-900"
                      : "border-slate-200 hover:border-slate-300 hover:bg-slate-50"
                  }`}
                  onClick={() => setSelectedCi(ciId)}
                >
                  <div className="font-medium">{ciId}</div>
                  <div className="text-sm text-slate-500">
                    {(applications as any[])?.filter((app: any) => app.ciId === ciId).length || 0} applications
                  </div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Connector Configuration */}
      <div className="lg:col-span-2">
        <Card className="card-modern">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center space-x-2">
                <SettingsIcon className="h-5 w-5" />
                <span>Tool Connectors</span>
                {selectedCi && (
                  <Badge variant="outline" className="ml-2">{selectedCi}</Badge>
                )}
              </CardTitle>
              {selectedCi && (
                <Button onClick={handleCreateConnector} size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Connector
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {!selectedCi ? (
              <div className="text-center py-12 text-slate-500">
                <SettingsIcon className="h-12 w-12 mx-auto mb-4 text-slate-300" />
                <p>Select a CI to view and manage connectors</p>
              </div>
            ) : (
              <div className="space-y-4">
                {(connectors as any[])?.length > 0 ? (
                  (connectors as any[]).map((connector: any) => {
                    const config = connectorConfigs.find(c => c.type === connector.connectorType);
                    return (
                      <div key={connector.id} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            {config?.icon}
                            <div>
                              <h3 className="font-medium">{config?.name}</h3>
                              <p className="text-sm text-slate-500">
                                Status: <Badge variant={
                                  connector.status === 'active' ? 'default' :
                                  connector.status === 'failed' ? 'destructive' : 'secondary'
                                }>
                                  {connector.status}
                                </Badge>
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => testConnectorMutation.mutate(connector.id)}
                              disabled={testConnectorMutation.isPending}
                              title="Test connection"
                            >
                              {testConnectorMutation.isPending ? (
                                <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                              ) : (
                                <CheckCircle className="h-4 w-4" />
                              )}
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleEditConnector(connector)}
                            >
                              <Edit2 className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => deleteConnectorMutation.mutate(connector.id)}
                              className="text-red-500 hover:text-red-700"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="text-center py-8 text-slate-500">
                    <p>No connectors configured for this CI</p>
                    <Button onClick={handleCreateConnector} className="mt-4">
                      Add First Connector
                    </Button>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );

  const renderDatabaseContent = () => (
    <Card className="card-modern">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <Database className="h-5 w-5" />
            <span>Database Health Check</span>
          </CardTitle>
          <Button 
            onClick={() => refetchDbHealth()} 
            size="sm" 
            variant="outline"
            disabled={dbHealthLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${dbHealthLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {dbHealthLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-slate-600">Checking database connectivity...</p>
          </div>
        ) : dbHealth ? (
          <div className="space-y-4">
            {/* Overall Status */}
            <div className="flex items-center space-x-3 p-4 rounded-lg border bg-slate-50">
              {dbHealth.status === 'healthy' ? (
                <CheckCircle className="h-6 w-6 text-green-600" />
              ) : (
                <XCircle className="h-6 w-6 text-red-600" />
              )}
              <div>
                <h3 className="font-semibold">
                  Database Status: {dbHealth.status === 'healthy' ? 'Healthy' : 'Error'}
                </h3>
                <p className="text-sm text-slate-600">{dbHealth.message}</p>
              </div>
              <div className="ml-auto">
                <Badge variant={dbHealth.status === 'healthy' ? 'default' : 'destructive'}>
                  HTTP {dbHealth.httpStatus}
                </Badge>
              </div>
            </div>

            {/* Connection Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">Connection Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-slate-600">Database URL Present:</span>
                    <Badge variant={dbHealth.database_url_present ? 'default' : 'secondary'}>
                      {dbHealth.database_url_present ? 'Yes' : 'No'}
                    </Badge>
                  </div>
                  {dbHealth.connection_test && (
                    <div className="flex justify-between">
                      <span className="text-sm text-slate-600">Connection Test:</span>
                      <Badge variant={dbHealth.connection_test === 'passed' ? 'default' : 'destructive'}>
                        {dbHealth.connection_test}
                      </Badge>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-sm text-slate-600">Timestamp:</span>
                    <span className="text-sm font-mono">
                      {dbHealth.timestamp ? new Date(dbHealth.timestamp).toLocaleString() : 'N/A'}
                    </span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">Database Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {dbHealth.database_version && (
                    <div>
                      <span className="text-sm text-slate-600">Version:</span>
                      <p className="text-sm font-mono bg-slate-100 p-1 rounded mt-1">
                        {dbHealth.database_version.split(' ').slice(0, 2).join(' ')}
                      </p>
                    </div>
                  )}
                  {dbHealth.tables_count !== undefined && (
                    <div className="flex justify-between">
                      <span className="text-sm text-slate-600">Tables Found:</span>
                      <Badge variant="outline">{dbHealth.tables_count}</Badge>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Tables Information */}
            {dbHealth.existing_tables && dbHealth.existing_tables.length > 0 && (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">Application Tables</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {dbHealth.existing_tables.map((table: string) => (
                      <Badge key={table} variant="outline" className="font-mono">
                        {table}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Error Details */}
            {dbHealth.status === 'error' && dbHealth.error_details && (
              <Card className="border-red-200">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm text-red-600 flex items-center">
                    <AlertCircle className="h-4 w-4 mr-2" />
                    Error Details
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm font-mono bg-red-50 p-3 rounded border text-red-700">
                    {dbHealth.error_details}
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        ) : (
          <div className="text-center py-8 text-slate-500">
            <AlertCircle className="h-12 w-12 mx-auto mb-4 text-slate-300" />
            <p>Unable to load database status</p>
          </div>
        )}
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate("/")}
              className="text-slate-600 hover:text-slate-900"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Settings
              </h1>
              <p className="text-slate-600">Manage system configuration and connectivity</p>
            </div>
          </div>
        </div>

        <div className="flex gap-6">
          {/* Left Sidebar */}
          <div className="w-64 flex-shrink-0">
            <Card className="card-modern">
              <CardHeader>
                <CardTitle className="text-lg">Settings Menu</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <nav className="space-y-1">
                  <button
                    className={`w-full text-left px-4 py-3 flex items-center space-x-3 transition-colors ${
                      activeMenuItem === "connectors" 
                        ? "bg-blue-50 text-blue-700 border-r-2 border-blue-500" 
                        : "hover:bg-slate-50"
                    }`}
                    onClick={() => setActiveMenuItem("connectors")}
                  >
                    <SettingsIcon className="h-5 w-5" />
                    <div>
                      <div className="font-medium">CI Connectors</div>
                      <div className="text-xs text-slate-500">Manage tool configurations</div>
                    </div>
                  </button>
                  <Separator />
                  <button
                    className={`w-full text-left px-4 py-3 flex items-center space-x-3 transition-colors ${
                      activeMenuItem === "database" 
                        ? "bg-blue-50 text-blue-700 border-r-2 border-blue-500" 
                        : "hover:bg-slate-50"
                    }`}
                    onClick={() => setActiveMenuItem("database")}
                  >
                    <Activity className="h-5 w-5" />
                    <div>
                      <div className="font-medium">Database Health</div>
                      <div className="text-xs text-slate-500">Test connectivity</div>
                    </div>
                  </button>
                </nav>
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {activeMenuItem === "connectors" && renderConnectorsContent()}
            {activeMenuItem === "database" && renderDatabaseContent()}
          </div>
        </div>

        {/* Create/Edit Connector Dialog */}
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>
                {editingConnector ? "Edit Connector" : "Create New Connector"}
              </DialogTitle>
            </DialogHeader>
            
            <div className="space-y-4">
              <div>
                <Label htmlFor="connectorType">Connector Type</Label>
                <Select value={selectedConnectorType} onValueChange={setSelectedConnectorType}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select connector type" />
                  </SelectTrigger>
                  <SelectContent>
                    {connectorConfigs.map((config) => (
                      <SelectItem key={config.type} value={config.type}>
                        <div className="flex items-center space-x-2">
                          {config.icon}
                          <span>{config.name}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {selectedConnectorConfig && (
                <div className="space-y-4">
                  <h4 className="font-medium">Configuration</h4>
                  {selectedConnectorConfig.fields.map((field) => (
                    <div key={field.key}>
                      <Label htmlFor={field.key}>
                        {field.label}
                        {field.required && <span className="text-red-500 ml-1">*</span>}
                      </Label>
                      <Input
                        id={field.key}
                        type={field.type}
                        placeholder={field.placeholder}
                        value={formData[field.key] || ""}
                        onChange={(e) => setFormData(prev => ({ ...prev, [field.key]: e.target.value }))}
                      />
                    </div>
                  ))}
                </div>
              )}

              <div className="flex justify-end space-x-2 pt-4">
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button 
                  onClick={handleSaveConnector}
                  disabled={!selectedConnectorType || saveConnectorMutation.isPending}
                >
                  {saveConnectorMutation.isPending ? "Saving..." : editingConnector ? "Update" : "Create"}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}