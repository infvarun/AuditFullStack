import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Rocket } from "lucide-react";
import { z } from "zod";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "../ui/form";
import { Input } from "../ui/input";
import { Checkbox } from "../ui/checkbox";
import { apiRequest, queryClient } from "../../lib/queryClient";
import { useToast } from "../../hooks/use-toast";
import { Application } from "@shared/schema";

const applicationSchema = z.object({
  auditName: z.string().min(1, "Audit name is required"),
  name: z.string().min(1, "Application name is required"),
  startDate: z.string().min(1, "Start date is required"),
  endDate: z.string().min(1, "End date is required"),
  ciId: z.string().min(1, "CI ID is required"),
  settings: z.object({
    enableFollowUpQuestions: z.boolean(),
    emailNotifications: z.boolean(),
  }),
});

type ApplicationFormData = z.infer<typeof applicationSchema>;

interface StepOneProps {
  applicationId: number | null;
  setApplicationId: (id: number) => void;
  onNext: () => void;
  setCanProceed: (canProceed: boolean) => void;
}

export default function StepOne({ applicationId, setApplicationId, onNext, setCanProceed }: StepOneProps) {
  const { toast } = useToast();
  const [isAuditInitiated, setIsAuditInitiated] = useState(false);
  
  // Query to fetch existing application data
  const { data: existingApplication, isLoading: isLoadingApplication } = useQuery<Application>({
    queryKey: [`/api/applications/${applicationId}`],
    enabled: !!applicationId,
  });
  
  const form = useForm<ApplicationFormData>({
    resolver: zodResolver(applicationSchema),
    defaultValues: {
      auditName: "",
      name: "",
      startDate: "",
      endDate: "",
      ciId: "",
      settings: {
        enableFollowUpQuestions: true,
        emailNotifications: true,
      },
    },
  });

  // Populate form with existing application data
  useEffect(() => {
    if (existingApplication) {
      console.log("Populating form with existing application data:", existingApplication);
      form.reset({
        auditName: existingApplication.auditName || "",
        name: existingApplication.name || existingApplication.auditName || "",
        startDate: (existingApplication as any).auditDateFrom || existingApplication.startDate || "",
        endDate: (existingApplication as any).auditDateTo || existingApplication.endDate || "",
        ciId: existingApplication.ciId || "",
        settings: {
          enableFollowUpQuestions: (existingApplication as any).enableFollowupQuestions ?? (existingApplication.settings as any)?.enableFollowUpQuestions ?? true,
          emailNotifications: (existingApplication.settings as any)?.emailNotifications ?? true,
        },
      });
      setIsAuditInitiated(true); // Mark as initiated since it already exists
    }
  }, [existingApplication, form]);

  // Only allow proceeding to next step after audit is initiated
  useEffect(() => {
    setCanProceed(isAuditInitiated);
  }, [isAuditInitiated, setCanProceed]);

  const createApplicationMutation = useMutation({
    mutationFn: async (data: ApplicationFormData) => {
      try {
        console.log("Making API request with data:", data);
        const method = existingApplication ? "PUT" : "POST";
        const url = existingApplication ? `/api/applications/${existingApplication.id}` : "/api/applications";
        const response = await apiRequest(method, url, data);
        console.log("Response received:", response.status, response.ok);
        const result = await response.json();
        console.log("Response JSON:", result);
        return result;
      } catch (error) {
        console.error("API request failed:", error);
        throw error;
      }
    },
    onSuccess: (data) => {
      console.log("Mutation success, application created/updated:", data);
      setApplicationId(data.id);
      setIsAuditInitiated(true);
      
      // Invalidate relevant caches to ensure Dashboard and Step 2 see the updated application
      queryClient.invalidateQueries({ queryKey: ["/api/applications"] }); // Main applications list
      queryClient.invalidateQueries({ queryKey: ["/api/applications", data.id] });
      queryClient.invalidateQueries({ queryKey: [`/api/applications/${data.id}`] });
      
      toast({
        title: existingApplication ? "Application updated successfully" : "Audit initiated successfully",
        description: existingApplication ? "Your audit application has been updated." : "Your audit application has been configured.",
      });
    },
    onError: (error) => {
      console.log("Mutation error:", error);
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const onSubmit = (data: ApplicationFormData) => {
    console.log("Form submission triggered with data:", data);
    createApplicationMutation.mutate(data);
  };

  // Clean up old window-based submission logic - no longer needed with direct form button

  // Show loading state while fetching existing application
  if (isLoadingApplication) {
    return (
      <div className="space-y-8">
        <Card className="card-modern">
          <CardContent className="p-8">
            <div className="animate-pulse space-y-4">
              <div className="h-4 bg-slate-200 rounded w-3/4"></div>
              <div className="h-10 bg-slate-200 rounded"></div>
              <div className="h-10 bg-slate-200 rounded"></div>
              <div className="grid grid-cols-2 gap-4">
                <div className="h-10 bg-slate-200 rounded"></div>
                <div className="h-10 bg-slate-200 rounded"></div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <Card className="card-modern">
        <CardHeader>
          <CardTitle className="flex items-center space-x-3">
            <Rocket className="h-5 w-5 text-purple-600" />
            <span className="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              Application Onboarding
            </span>
          </CardTitle>
          <p className="text-sm text-slate-600">
            Configure your audit application settings and parameters
          </p>
        </CardHeader>
        
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="auditName"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      Audit Name <span className="text-red-500">*</span>
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Enter audit name (e.g., Q1 2024 Compliance Audit)"
                        className="input-modern"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Name for this audit session
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      Application Name <span className="text-red-500">*</span>
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Enter application name (e.g., Customer Portal)"
                        className="input-modern"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Application being audited
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="startDate"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>
                        Audit Start Date <span className="text-red-500">*</span>
                      </FormLabel>
                      <FormControl>
                        <Input type="date" className="input-modern" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="endDate"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>
                        Audit End Date <span className="text-red-500">*</span>
                      </FormLabel>
                      <FormControl>
                        <Input type="date" className="input-modern" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="ciId"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      Configuration Item (CI) ID <span className="text-red-500">*</span>
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Enter CI ID (e.g., CI-12345)"
                        className="input-modern"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Configuration Management Database identifier
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 border border-purple-200">
                <h3 className="text-sm font-medium bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-3">
                  Additional Settings
                </h3>
                <div className="space-y-3">
                  <FormField
                    control={form.control}
                    name="settings.enableFollowUpQuestions"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-center space-x-3 space-y-0">
                        <FormControl>
                          <Checkbox
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                        </FormControl>
                        <FormLabel className="text-sm">
                          Enable follow-up questions
                        </FormLabel>
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="settings.emailNotifications"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-center space-x-3 space-y-0">
                        <FormControl>
                          <Checkbox
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                        </FormControl>
                        <FormLabel className="text-sm">
                          Email notifications on completion
                        </FormLabel>
                      </FormItem>
                    )}
                  />
                </div>
              </div>

              {/* Initiate Audit Button */}
              <div className="flex justify-center pt-4">
                <button
                  type="submit"
                  disabled={createApplicationMutation.isPending || (isAuditInitiated && !existingApplication)}
                  className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 disabled:from-gray-400 disabled:to-gray-500 text-white px-8 py-3 rounded-xl font-medium shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed"
                >
                  {createApplicationMutation.isPending ? (
                    <span className="flex items-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Initiating Audit...
                    </span>
                  ) : isAuditInitiated ? (
                    <span className="flex items-center">
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      {existingApplication ? "Update Now" : "Audit Initiated"}
                    </span>
                  ) : (
                    existingApplication ? "Update Application" : "Initiate Audit"
                  )}
                </button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
