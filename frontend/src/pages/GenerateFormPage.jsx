import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import GrievanceForm from '../components/GrievanceForm';
import GrievanceLetterEditor from '../components/GrievanceLetterEditor';
import { useGenerateGrievance, useCreateGrievance } from '../hooks/useGrievances';
import { useAuth } from '../context/AuthContext';

export default function GenerateFormPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState(null);
  const [generatedData, setGeneratedData] = useState(null);
  const [apiError, setApiError] = useState('');

  const generateMutation = useGenerateGrievance();
  const createMutation = useCreateGrievance();

  const handleGenerate = async (data) => {
    try {
      setApiError('');
      setFormData(data);
      const result = await generateMutation.mutateAsync(data);
      setGeneratedData(result.generated);
      setStep(2);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      if (err.response?.status === 429) {
        setApiError('You have reached your daily limit for generating grievances. Please try again tomorrow.');
      } else {
        setApiError(err.response?.data?.detail || 'Failed to generate letter. Please try again.');
      }
    }
  };

  const handleSave = async (editData) => {
    try {
      setApiError('');
      const finalPayload = {
        ...formData,
        ...generatedData,
        ...editData, // overrides subject_line, letter_body, status
      };
      
      const newGrievance = await createMutation.mutateAsync(finalPayload);
      navigate(`/grievances/${newGrievance.id}`);
    } catch (err) {
      setApiError(err.response?.data?.detail || 'Failed to save grievance. Please try again.');
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-100 mb-2">
          {step === 1 ? 'New Grievance' : 'Review Your Letter'}
        </h1>
        <p className="text-slate-400">
          {step === 1 
            ? 'Provide the details below and our AI will draft a professional complaint letter.'
            : 'Review and edit the AI-generated letter before saving it.'}
        </p>
      </div>

      {/* Error Banner */}
      {apiError && (
        <div className="mb-6 bg-red-900/30 border border-red-500/50 rounded-xl p-4 flex items-start gap-3">
          <span className="material-icons text-red-400">error_outline</span>
          <p className="text-red-200">{apiError}</p>
        </div>
      )}

      {/* Step Content */}
      <div className="relative">
        {step === 1 && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <GrievanceForm 
              onSubmit={handleGenerate} 
              isSubmitting={generateMutation.isPending}
              defaultValues={{
                contact_name: user?.full_name || '',
                contact_email: user?.email || '',
              }}
            />
          </div>
        )}

        {step === 2 && generatedData && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 space-y-6">
            <GrievanceLetterEditor
              generatedData={generatedData}
              companyName={formData.company_name}
              contactName={formData.contact_name}
              onSave={handleSave}
              isSaving={createMutation.isPending}
            />
            
            <div className="flex justify-center">
              <button
                onClick={() => setStep(1)}
                disabled={createMutation.isPending}
                className="text-slate-400 hover:text-slate-200 transition-colors text-sm font-medium disabled:opacity-50"
              >
                ← Back to edit details
              </button>
            </div>
          </div>
        )}
      </div>

    </div>
  );
}
