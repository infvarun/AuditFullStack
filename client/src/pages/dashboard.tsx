import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link, useLocation } from "wouter";
import { 
  Search, 
  Plus, 
  Settings, 
  User, 
  Calendar, 
  FileText, 
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  Bot
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Application } from "@shared/schema";

export default function Dashboard() {
  const [, setLocation] = useLocation();
  const [searchQuery, setSearchQuery] = useState("");

  // Fetch all applications
  const { data: applications = [], isLoading } = useQuery<Application[]>({
    queryKey: ["/api/applications"],
    enabled: true,
  });

  // Filter applications based on search
  const filteredApplications = applications.filter(app => 
    app.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    app.ciId.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Get recent applications (last 3)
  const recentApplications = applications.slice(-3);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "text-green-600 bg-green-50";
      case "in_progress": return "text-blue-600 bg-blue-50";
      case "pending": return "text-yellow-600 bg-yellow-50";
      default: return "text-gray-600 bg-gray-50";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed": return <CheckCircle className="h-4 w-4" />;
      case "in_progress": return <Clock className="h-4 w-4" />;
      case "pending": return <AlertCircle className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Navigation Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-white" />
              </div>
              <h1 className="text-xl font-bold text-slate-900">CA Audit Agent</h1>
            </div>

            {/* Right side actions */}
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" className="text-slate-600">
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
              <Avatar className="h-8 w-8">
                <AvatarFallback className="bg-gradient-to-br from-purple-600 to-blue-600 text-white text-sm">
                  <User className="h-4 w-4" />
                </AvatarFallback>
              </Avatar>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Section */}
        <div className="mb-8">
          <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-6 shadow-sm border border-white/20">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Find ongoing audit</h2>
            
            <div className="relative mb-6">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search applications by name or CI ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 h-12 text-sm border-slate-200 focus:border-purple-500 focus:ring-purple-500"
              />
            </div>

            {/* Search Results */}
            {searchQuery && (
              <div className="space-y-3 mb-6">
                {filteredApplications.length > 0 ? (
                  filteredApplications.map((app) => (
                    <div
                      key={app.id}
                      className="flex items-center justify-between p-4 bg-white rounded-lg border border-slate-200 hover:shadow-sm transition-shadow cursor-pointer"
                      onClick={() => setLocation(`/wizard/${app.id}`)}
                    >
                      <div>
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="font-medium text-slate-900">{app.name}</span>
                          <Badge variant="outline" className="text-xs">
                            {app.ciId}
                          </Badge>
                        </div>
                        <div className="flex items-center space-x-4 text-sm text-slate-600">
                          <span className="flex items-center">
                            <Calendar className="h-3 w-3 mr-1" />
                            {app.startDate && app.endDate ? 
                              `${new Date(app.startDate).toLocaleDateString()} - ${new Date(app.endDate).toLocaleDateString()}` : 
                              'Date not set'
                            }
                          </span>
                          <span className="flex items-center">
                            <Clock className="h-3 w-3 mr-1" />
                            {app.createdAt ? new Date(app.createdAt).toLocaleDateString() : 'Recently created'}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs ${getStatusColor("in_progress")}`}>
                          {getStatusIcon("in_progress")}
                          <span>In Progress</span>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-slate-500">
                    No applications found matching "{searchQuery}"
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Create First Audit Button */}
        <div className="mb-8 text-center">
          <Button
            onClick={() => setLocation("/wizard")}
            className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white px-8 py-6 text-lg font-medium rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
          >
            <Bot className="h-6 w-6 mr-3" />
            Create First Audit
          </Button>
        </div>

        {/* Recent Audits */}
        <div>
          <h2 className="text-2xl font-bold text-slate-900 mb-6">Recent Audits</h2>
          
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <Card key={i} className="animate-pulse">
                  <CardContent className="p-6">
                    <div className="h-4 bg-slate-200 rounded mb-2"></div>
                    <div className="h-3 bg-slate-200 rounded mb-4"></div>
                    <div className="h-20 bg-slate-200 rounded"></div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : recentApplications.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recentApplications.map((app) => (
                <Card 
                  key={app.id} 
                  className="bg-gradient-to-br from-blue-500 to-blue-600 text-white hover:shadow-lg transition-shadow cursor-pointer transform hover:scale-105 duration-200"
                  onClick={() => setLocation(`/wizard/${app.id}`)}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg font-semibold text-white">
                        {app.name}
                      </CardTitle>
                      <Badge variant="secondary" className="bg-white/20 text-white border-white/30">
                        {app.ciId}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <h3 className="font-semibold text-white mb-2">Primary audit details</h3>
                    <p className="text-blue-100 text-sm leading-relaxed">
                      Audit period: {app.startDate && app.endDate ? 
                        `${new Date(app.startDate).toLocaleDateString()} - ${new Date(app.endDate).toLocaleDateString()}` : 
                        'Date not set'
                      }
                      <br />
                      Created: {app.createdAt ? new Date(app.createdAt).toLocaleDateString() : 'Recently created'}
                      <br />
                      Status: In Progress
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="relative mb-6">
                <Bot className="h-24 w-24 text-blue-300 mx-auto mb-4" />
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs font-bold">AI</span>
                </div>
              </div>
              <h3 className="text-lg font-medium text-slate-900 mb-2">AI Agent Ready</h3>
              <p className="text-slate-500 mb-6">Your intelligent audit assistant is ready to help you get started</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}