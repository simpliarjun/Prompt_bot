import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import { StatusBadge, SeverityBadge } from './Badges';

export default function GrievanceCard({ grievance }) {
  const {
    id,
    company_name,
    product_or_service,
    subject_line,
    status,
    severity,
    incident_date,
    created_at,
  } = grievance;

  return (
    <Link
      to={`/grievances/${id}`}
      className="block group bg-slate-800/50 hover:bg-slate-800 border border-slate-700/50 hover:border-blue-500/50 rounded-xl p-5 transition-all duration-200 hover:shadow-lg hover:shadow-blue-500/10"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0 pr-4">
          <h3 className="text-lg font-medium text-slate-100 truncate group-hover:text-blue-400 transition-colors">
            {company_name}
          </h3>
          <p className="text-sm text-slate-400 truncate">
            {product_or_service}
          </p>
        </div>
        <div className="flex flex-col gap-2 items-end shrink-0">
          <StatusBadge status={status} />
          <SeverityBadge severity={severity} />
        </div>
      </div>

      <div className="mb-4">
        <p className="text-sm text-slate-300 line-clamp-2">
          {subject_line}
        </p>
      </div>

      <div className="flex items-center justify-between text-xs text-slate-500 border-t border-slate-700/50 pt-3">
        <div className="flex items-center gap-1.5">
          <span className="material-icons text-[14px]">event</span>
          <span>Incident: {format(new Date(incident_date), 'MMM d, yyyy')}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="material-icons text-[14px]">history</span>
          <span>Created: {format(new Date(created_at), 'MMM d, yyyy')}</span>
        </div>
      </div>
    </Link>
  );
}
