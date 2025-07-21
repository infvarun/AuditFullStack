import { useState, useEffect } from "react";
import { useParams } from "wouter";
import { useQuery } from "@tanstack/react-query";
import { Link } from "wouter";
import { ArrowLeft, Settings, User, TrendingUp } from "lucide-react";
import { Button } from "../components/ui/button";
import { Avatar, AvatarFallback } from "../components/ui/avatar";
import ProgressBar from "../components/wizard/progress-bar";
import Navigation from "../components/wizard/navigation";
import StepOne from "../components/wizard/step-one";
import StepTwo from "../components/wizard/step-two";
import StepThree from "../components/wizard/step-three-new";
import StepFour from "../components/wizard/step-four";
import StepFive from "../components/wizard/step-five";
import { Application } from "@shared/schema";

const steps = [
  { id: 1, title: "Application Setup", component: StepOne },
  { id: 2, title: "Data Request", component: StepTwo },
  { id: 3, title: "Question Analysis", component: StepThree },
  { id: 4, title: "Data Collection", component: StepFour },
  { id: 5, title: "Results", component: StepFive },
];

export default function WizardPage() {
  const params = useParams();
  const existingAppId = params.applicationId ? parseInt(params.applicationId) : null;
  
  const [currentStep, setCurrentStep] = useState(1);
  const [applicationId, setApplicationId] = useState<number | null>(existingAppId);
  const [canProceed, setCanProceed] = useState(false);

  // Load existing application if ID is provided
  const { data: existingApplication } = useQuery<Application>({
    queryKey: [`/api/applications/${existingAppId}`],
    enabled: !!existingAppId,
  });

  // Set application ID when existing app is loaded
  useEffect(() => {
    if (existingApplication) {
      setApplicationId(existingApplication.id);
    }
  }, [existingApplication]);

  const handleNext = () => {
    console.log("Next button clicked, current step:", currentStep);
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
      setCanProceed(true); // Always allow proceeding
    }
  };

  const advanceStep = () => {
    console.log("Advancing step from", currentStep, "to", currentStep + 1);
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
      setCanProceed(false); // Reset for next step
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      setCanProceed(true); // Allow going back
    }
  };

  const currentStepData = steps.find(step => step.id === currentStep);
  const CurrentStepComponent = currentStepData?.component;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100">
      {/* Navigation Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo and Back Button */}
            <div className="flex items-center space-x-4">
              <Link href="/">
                <Button variant="ghost" size="sm" className="flex items-center space-x-2 text-slate-600 hover:text-slate-900">
                  <ArrowLeft className="h-4 w-4" />
                  <span>Back to Dashboard</span>
                </Button>
              </Link>
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg flex items-center justify-center">
                  <TrendingUp className="h-5 w-5 text-white" />
                </div>
                <h1 className="text-xl font-bold text-slate-900">
                  {existingApplication ? `${existingApplication.name} - Audit Wizard` : 'New Audit Wizard'}
                </h1>
              </div>
            </div>

            {/* Right side actions */}
            <div className="flex items-center space-x-4">
              <Link href="/settings">
                <Button variant="ghost" size="sm" className="text-slate-600 hover:text-slate-900">
                  <Settings className="h-4 w-4 mr-2" />
                  Settings
                </Button>
              </Link>
              <Avatar className="h-8 w-8">
                <AvatarFallback className="bg-gradient-to-br from-purple-600 to-blue-600 text-white text-sm">
                  <User className="h-4 w-4" />
                </AvatarFallback>
              </Avatar>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <ProgressBar currentStep={currentStep} totalSteps={steps.length} steps={steps} />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {CurrentStepComponent && (
          <CurrentStepComponent
            applicationId={applicationId}
            setApplicationId={setApplicationId}
            onNext={currentStep === 1 ? advanceStep : handleNext}
            setCanProceed={setCanProceed}
          />
        )}

        {/* Navigation */}
        <Navigation
          currentStep={currentStep}
          totalSteps={steps.length}
          onNext={handleNext}
          onPrevious={handlePrevious}
          canProceed={canProceed}
        />
      </main>
    </div>
  );
}
