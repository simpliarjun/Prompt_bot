import { useState, useEffect } from 'react';
import { SeverityBadge } from './Badges';

export default function GrievanceLetterEditor({ 
  generatedData, 
  onSave, 
  isSaving,
  companyName,
  contactName,
  hideActions = false
}) {
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');

  // Sync initial data
  useEffect(() => {
    if (generatedData) {
      setSubject(generatedData.subject_line || '');
      setBody(generatedData.letter_body || '');
    }
  }, [generatedData]);

  if (!generatedData) return null;

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden shadow-xl shadow-black/20">
      {/* Header Info */}
      <div className="p-6 bg-slate-800/80 border-b border-slate-700">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <h2 className="text-xl font-semibold text-slate-100 flex items-center gap-2">
            <span className="material-icons text-indigo-400">description</span>
            Generated Letter
          </h2>
          <div className="flex items-center gap-4">
            <div className="text-sm">
              <span className="text-slate-400">Target SLA: </span>
              <span className="font-medium text-slate-200">{generatedData.suggested_sla_hours} hours</span>
            </div>
            <SeverityBadge severity={generatedData.severity} />
          </div>
        </div>

        {/* Key Facts Summary */}
        <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700/50">
          <h4 className="text-sm font-medium text-slate-300 mb-2 flex items-center gap-1.5">
            <span className="material-icons text-[16px] text-indigo-400">psychology</span>
            AI Key Facts Extraction
          </h4>
          <ul className="space-y-1.5">
            {generatedData.key_facts_summary?.map((fact, idx) => (
              <li key={idx} className="text-sm text-slate-400 flex items-start gap-2">
                <span className="text-indigo-500 mt-0.5">•</span>
                <span>{fact}</span>
              </li>
            ))}
          </ul>
        </div>
        
        {generatedData.tone_note && (
          <div className="mt-3 text-sm text-amber-400/90 flex items-start gap-1.5 bg-amber-900/10 p-3 rounded-lg border border-amber-900/20">
            <span className="material-icons text-[18px]">info</span>
            <span>{generatedData.tone_note}</span>
          </div>
        )}
      </div>

      {/* Editor Area */}
      <div className="p-6 space-y-6">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Subject Line</label>
          <input
            type="text"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            readOnly={hideActions}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-slate-100 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors font-medium"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2 flex items-center justify-between">
            <span>Letter Body</span>
            {!hideActions && <span className="text-xs text-indigo-400 font-normal">Feel free to edit the text below</span>}
          </label>
          
          <div className="bg-slate-900 border border-slate-700 rounded-lg overflow-hidden focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500 transition-colors">
            {/* Contextual template boundaries */}
            <div className="px-4 py-3 bg-slate-800/50 border-b border-slate-700/50 text-slate-400 text-sm font-mono select-none">
              Dear {companyName || '[Company]'} Customer Relations Team,
            </div>
            
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              readOnly={hideActions}
              rows="12"
              className="w-full bg-transparent border-none px-4 py-4 text-slate-200 focus:ring-0 resize-y leading-relaxed"
            />
            
            <div className="px-4 py-3 bg-slate-800/50 border-t border-slate-700/50 text-slate-400 text-sm font-mono select-none">
              Sincerely,<br />
              {contactName || '[Your Name]'}
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      {!hideActions && (
        <div className="p-6 bg-slate-800/80 border-t border-slate-700 flex justify-end gap-4">
          <button
            onClick={() => onSave({ subject_line: subject, letter_body: body, status: 'draft' })}
            disabled={isSaving}
            className="px-6 py-2.5 rounded-lg text-sm font-medium text-slate-300 bg-slate-700 hover:bg-slate-600 transition-colors disabled:opacity-50"
          >
            Save as Draft
          </button>
          
          <button
            onClick={() => onSave({ subject_line: subject, letter_body: body, status: 'finalized' })}
            disabled={isSaving}
            className="px-6 py-2.5 rounded-lg text-sm font-medium text-white bg-gradient-to-r from-indigo-500 to-indigo-600 hover:from-indigo-600 hover:to-indigo-700 transition-all shadow-lg shadow-indigo-500/25 disabled:opacity-50 flex items-center gap-2"
          >
            {isSaving && (
              <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            )}
            Save and Finalize
          </button>
        </div>
      )}
    </div>
  );
}
