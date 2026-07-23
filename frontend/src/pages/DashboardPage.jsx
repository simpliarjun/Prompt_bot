import { useState } from 'react';
import { useGrievances, useGrievanceStats } from '../hooks/useGrievances';
import GrievanceCard from '../components/GrievanceCard';
import EmptyState from '../components/EmptyState';
import { useAuth } from '../context/AuthContext';

export default function DashboardPage() {
  const { user } = useAuth();
  const [statusFilter, setStatusFilter] = useState('');
  
  // Queries
  const { data: grievancesData, isLoading: isLoadingList, isError } = useGrievances(
    statusFilter ? { status: statusFilter } : {}
  );
  const { data: statsData } = useGrievanceStats();

  const handleFilterClick = (status) => {
    setStatusFilter(prev => prev === status ? '' : status);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      
      {/* Header */}
      <div className="mb-10">
        <h1 className="text-3xl font-bold text-slate-100">Welcome back, {user?.full_name?.split(' ')[0]}</h1>
        <p className="text-slate-400 mt-2">Manage and track your consumer grievances.</p>
      </div>

      {/* Stats Summary */}
      {statsData && statsData.total > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-10">
          <button 
            onClick={() => setStatusFilter('')}
            className={`p-4 rounded-xl border text-left transition-all ${statusFilter === '' ? 'bg-indigo-500/10 border-indigo-500/50 ring-1 ring-indigo-500' : 'bg-slate-800/50 border-slate-700 hover:border-slate-600'}`}
          >
            <p className="text-sm font-medium text-slate-400">Total</p>
            <p className="text-2xl font-semibold text-slate-100">{statsData.total}</p>
          </button>
          <button 
            onClick={() => handleFilterClick('draft')}
            className={`p-4 rounded-xl border text-left transition-all ${statusFilter === 'draft' ? 'bg-indigo-500/10 border-indigo-500/50 ring-1 ring-indigo-500' : 'bg-slate-800/50 border-slate-700 hover:border-slate-600'}`}
          >
            <p className="text-sm font-medium text-slate-400">Drafts</p>
            <p className="text-2xl font-semibold text-slate-100">{statsData.draft}</p>
          </button>
          <button 
            onClick={() => handleFilterClick('finalized')}
            className={`p-4 rounded-xl border text-left transition-all ${statusFilter === 'finalized' ? 'bg-indigo-500/10 border-indigo-500/50 ring-1 ring-indigo-500' : 'bg-slate-800/50 border-slate-700 hover:border-slate-600'}`}
          >
            <p className="text-sm font-medium text-slate-400">Finalized</p>
            <p className="text-2xl font-semibold text-slate-100">{statsData.finalized}</p>
          </button>
          <button 
            onClick={() => handleFilterClick('resolved')}
            className={`p-4 rounded-xl border text-left transition-all ${statusFilter === 'resolved' ? 'bg-indigo-500/10 border-indigo-500/50 ring-1 ring-indigo-500' : 'bg-slate-800/50 border-slate-700 hover:border-slate-600'}`}
          >
            <p className="text-sm font-medium text-slate-400">Resolved</p>
            <p className="text-2xl font-semibold text-slate-100">{statsData.resolved}</p>
          </button>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-slate-100">
          {statusFilter ? `${statusFilter.charAt(0).toUpperCase() + statusFilter.slice(1)} Grievances` : 'Recent Grievances'}
        </h2>
        {statusFilter && (
          <button 
            onClick={() => setStatusFilter('')}
            className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors"
          >
            Clear Filter
          </button>
        )}
      </div>

      {isLoadingList ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-48 bg-slate-800/50 rounded-xl border border-slate-700 animate-pulse"></div>
          ))}
        </div>
      ) : isError ? (
        <div className="p-4 bg-red-900/30 border border-red-500/50 rounded-xl text-red-200">
          Failed to load grievances. Please try refreshing the page.
        </div>
      ) : grievancesData?.items?.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {grievancesData.items.map(grievance => (
            <GrievanceCard key={grievance.id} grievance={grievance} />
          ))}
        </div>
      ) : (
        <EmptyState />
      )}

    </div>
  );
}
