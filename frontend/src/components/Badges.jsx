const STATUS_CONFIG = {
  draft:     { label: 'Draft',     bg: 'bg-slate-700',   text: 'text-slate-300', icon: '📝' },
  finalized: { label: 'Finalized', bg: 'bg-indigo-900',  text: 'text-indigo-300', icon: '✅' },
  sent:      { label: 'Sent',      bg: 'bg-cyan-900',    text: 'text-cyan-300',   icon: '📨' },
  resolved:  { label: 'Resolved',  bg: 'bg-emerald-900', text: 'text-emerald-300', icon: '🎉' },
  escalated: { label: 'Escalated', bg: 'bg-amber-900',   text: 'text-amber-300',  icon: '⚠️' },
};

export function StatusBadge({ status }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.draft;
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${cfg.bg} ${cfg.text}`}
      role="status"
      aria-label={`Status: ${cfg.label}`}
    >
      <span aria-hidden="true">{cfg.icon}</span>
      {cfg.label}
    </span>
  );
}

const SEVERITY_CONFIG = {
  low:      { label: 'Low',      bg: 'bg-slate-700',    text: 'text-slate-300',  icon: '🟢' },
  medium:   { label: 'Medium',   bg: 'bg-amber-900/60', text: 'text-amber-300',  icon: '🟡' },
  high:     { label: 'High',     bg: 'bg-orange-900/60',text: 'text-orange-300', icon: '🟠' },
  critical: { label: 'Critical', bg: 'bg-red-900/60',   text: 'text-red-300',    icon: '🔴' },
};

export function SeverityBadge({ severity }) {
  const cfg = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.low;
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${cfg.bg} ${cfg.text}`}
      role="status"
      aria-label={`Severity: ${cfg.label}`}
    >
      <span aria-hidden="true">{cfg.icon}</span>
      {cfg.label}
    </span>
  );
}
