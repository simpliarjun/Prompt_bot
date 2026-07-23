import { Link } from 'react-router-dom';

export default function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center p-12 bg-slate-800/30 border border-slate-700/50 rounded-2xl text-center">
      <div className="w-20 h-20 bg-indigo-500/10 rounded-full flex items-center justify-center mb-6">
        <span className="text-4xl">📝</span>
      </div>
      <h3 className="text-xl font-semibold text-slate-100 mb-2">
        No grievances yet
      </h3>
      <p className="text-slate-400 max-w-md mb-8">
        Get started by filing your first grievance. Our AI will help you draft a professional, factual complaint ready to send to the company.
      </p>
      <Link
        to="/grievances/new"
        className="px-6 py-3 rounded-xl bg-indigo-500 text-white font-medium hover:bg-indigo-600 transition-all shadow-lg shadow-indigo-500/25"
      >
        File Your First Grievance
      </Link>
    </div>
  );
}
