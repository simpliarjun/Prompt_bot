import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { useGrievance, useUpdateGrievance, useDeleteGrievance, useExportPdf } from '../hooks/useGrievances';
import GrievanceLetterEditor from '../components/GrievanceLetterEditor';
import ConfirmDialog from '../components/ConfirmDialog';
import { StatusBadge, SeverityBadge } from '../components/Badges';

export default function ReportViewPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [isEditing, setIsEditing] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  
  // Queries & Mutations
  const { data: grievance, isLoading, isError } = useGrievance(id);
  const updateMutation = useUpdateGrievance();
  const deleteMutation = useDeleteGrievance();
  const exportMutation = useExportPdf();

  const handleUpdateStatus = async (newStatus) => {
    try {
      await updateMutation.mutateAsync({ id, data: { status: newStatus } });
    } catch (err) {
      console.error('Failed to update status:', err);
    }
  };

  const handleSaveEdits = async ({ subject_line, letter_body, status }) => {
    try {
      await updateMutation.mutateAsync({ id, data: { subject_line, letter_body, status } });
      setIsEditing(false);
    } catch (err) {
      console.error('Failed to save edits:', err);
    }
  };

  const handleDelete = async () => {
    try {
      await deleteMutation.mutateAsync(id);
      navigate('/');
    } catch (err) {
      console.error('Failed to delete:', err);
    }
  };

  const handleExport = async () => {
    try {
      await exportMutation.mutateAsync(id);
    } catch (err) {
      console.error('Failed to export PDF:', err);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-indigo-500 border-t-transparent" />
      </div>
    );
  }

  if (isError || !grievance) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <h2 className="text-2xl font-bold text-slate-100 mb-4">Grievance Not Found</h2>
        <p className="text-slate-400 mb-6">This grievance may have been deleted or you don't have access to it.</p>
        <button onClick={() => navigate('/')} className="text-indigo-400 hover:text-indigo-300">
          Return to Dashboard
        </button>
      </div>
    );
  }

  const isDraft = grievance.status === 'draft';

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      
      {/* Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 pb-6 border-b border-slate-700/50">
        <div className="flex items-center gap-3">
          <button 
            onClick={() => navigate('/')}
            className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 hover:text-slate-200 hover:bg-slate-700 transition-colors"
          >
            <span className="material-icons text-[20px]">arrow_back</span>
          </button>
          <div>
            <h1 className="text-2xl font-bold text-slate-100">Grievance Details</h1>
            <p className="text-sm text-slate-400">Created on {format(new Date(grievance.created_at), 'PPP')}</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Status Transitions */}
          {grievance.status === 'finalized' && (
            <button
              onClick={() => handleUpdateStatus('sent')}
              disabled={updateMutation.isPending}
              className="px-4 py-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 hover:bg-cyan-500/20 transition-colors text-sm font-medium disabled:opacity-50"
            >
              Mark as Sent
            </button>
          )}
          {grievance.status === 'sent' && (
            <>
              <button
                onClick={() => handleUpdateStatus('resolved')}
                disabled={updateMutation.isPending}
                className="px-4 py-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20 transition-colors text-sm font-medium disabled:opacity-50"
              >
                Mark Resolved
              </button>
              <button
                onClick={() => handleUpdateStatus('escalated')}
                disabled={updateMutation.isPending}
                className="px-4 py-2 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20 hover:bg-amber-500/20 transition-colors text-sm font-medium disabled:opacity-50"
              >
                Escalate
              </button>
            </>
          )}

          {/* Export */}
          <button
            onClick={handleExport}
            disabled={isDraft || exportMutation.isPending}
            title={isDraft ? "Cannot export draft grievances" : "Download PDF"}
            className="px-4 py-2 rounded-lg bg-indigo-500 text-white hover:bg-indigo-600 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {exportMutation.isPending ? (
              <span className="material-icons animate-spin text-[18px]">refresh</span>
            ) : (
              <span className="material-icons text-[18px]">picture_as_pdf</span>
            )}
            Export PDF
          </button>

          {/* Delete */}
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="w-10 h-10 rounded-lg bg-slate-800 text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors flex items-center justify-center"
            title="Delete Grievance"
          >
            <span className="material-icons text-[20px]">delete</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Letter Editor/View */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-xl font-semibold text-slate-100">Complaint Letter</h2>
            {(isDraft || grievance.status === 'finalized') && !isEditing && (
              <button
                onClick={() => setIsEditing(true)}
                className="text-sm font-medium text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
              >
                <span className="material-icons text-[16px]">edit</span> Edit Letter
              </button>
            )}
          </div>
          
          <GrievanceLetterEditor 
            generatedData={grievance}
            companyName={grievance.company_name}
            contactName={grievance.contact_name}
            hideActions={!isEditing}
            onSave={handleSaveEdits}
            isSaving={updateMutation.isPending}
          />
        </div>

        {/* Right Column: Metadata */}
        <div className="space-y-6">
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <h3 className="text-lg font-medium text-slate-100 mb-4">Metadata</h3>
            
            <dl className="space-y-4">
              <div>
                <dt className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">Status</dt>
                <dd><StatusBadge status={grievance.status} /></dd>
              </div>
              
              <div>
                <dt className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">Severity</dt>
                <dd><SeverityBadge severity={grievance.severity} /></dd>
              </div>

              <div className="pt-4 border-t border-slate-700">
                <dt className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">Company</dt>
                <dd className="text-sm text-slate-200">{grievance.company_name}</dd>
              </div>

              <div>
                <dt className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">Product/Service</dt>
                <dd className="text-sm text-slate-200">{grievance.product_or_service}</dd>
              </div>

              <div>
                <dt className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">Incident Date</dt>
                <dd className="text-sm text-slate-200">{format(new Date(grievance.incident_date), 'PPP')}</dd>
              </div>

              {grievance.order_reference && (
                <div>
                  <dt className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">Reference #</dt>
                  <dd className="text-sm text-slate-200">{grievance.order_reference}</dd>
                </div>
              )}
            </dl>
          </div>

          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <h3 className="text-lg font-medium text-slate-100 mb-4">Original Input</h3>
            <div className="prose prose-sm prose-invert max-w-none">
              <p className="text-slate-400 whitespace-pre-wrap italic">"{grievance.raw_description}"</p>
            </div>
            
            <div className="mt-4 pt-4 border-t border-slate-700">
              <span className="text-xs font-medium text-slate-400 uppercase tracking-wider block mb-1">Desired Resolution</span>
              <p className="text-sm text-slate-200 capitalize">
                {grievance.desired_resolution.replace('_', ' ')}
                {grievance.desired_resolution_details && ` — ${grievance.desired_resolution_details}`}
              </p>
            </div>
          </div>
        </div>
      </div>

      <ConfirmDialog
        isOpen={showDeleteConfirm}
        title="Delete Grievance"
        message="Are you sure you want to delete this grievance? This action cannot be undone."
        isDestructive={true}
        isPending={deleteMutation.isPending}
        onConfirm={handleDelete}
        onCancel={() => setShowDeleteConfirm(false)}
      />

    </div>
  );
}
