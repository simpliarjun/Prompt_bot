import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { grievanceGenerateSchema, CATEGORIES, RESOLUTIONS } from '../schemas/grievanceSchema';

export default function GrievanceForm({ onSubmit, defaultValues = {}, isSubmitting }) {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(grievanceGenerateSchema),
    defaultValues: {
      company_name: '',
      product_or_service: '',
      category: 'product_defect',
      incident_date: '',
      order_reference: '',
      raw_description: '',
      desired_resolution: 'refund',
      desired_resolution_details: '',
      contact_name: '',
      contact_email: '',
      contact_phone: '',
      ...defaultValues,
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* 1. Incident Details */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
        <h3 className="text-lg font-medium text-slate-100 mb-4">1. Incident Details</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Company Name *</label>
            <input
              {...register('company_name')}
              className={`w-full bg-slate-900 border ${errors.company_name ? 'border-red-500' : 'border-slate-700'} rounded-lg px-4 py-2.5 text-slate-100 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors`}
              placeholder="e.g. Acme Corp"
            />
            {errors.company_name && <p className="mt-1 text-sm text-red-400">{errors.company_name.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Product or Service *</label>
            <input
              {...register('product_or_service')}
              className={`w-full bg-slate-900 border ${errors.product_or_service ? 'border-red-500' : 'border-slate-700'} rounded-lg px-4 py-2.5 text-slate-100 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors`}
              placeholder="e.g. Wireless Router X200"
            />
            {errors.product_or_service && <p className="mt-1 text-sm text-red-400">{errors.product_or_service.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Category *</label>
            <select
              {...register('category')}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-slate-100 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
            >
              {CATEGORIES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Incident Date *</label>
            <input
              type="date"
              {...register('incident_date')}
              className={`w-full bg-slate-900 border ${errors.incident_date ? 'border-red-500' : 'border-slate-700'} rounded-lg px-4 py-2.5 text-slate-100 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors`}
            />
            {errors.incident_date && <p className="mt-1 text-sm text-red-400">{errors.incident_date.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Order / Reference # (Optional)</label>
            <input
              {...register('order_reference')}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-slate-100 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
              placeholder="e.g. ORD-123456"
            />
          </div>
        </div>
      </div>

      {/* 2. What Happened */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
        <h3 className="text-lg font-medium text-slate-100 mb-1">2. What Happened? *</h3>
        <p className="text-sm text-slate-400 mb-4">Describe the issue in your own words. Be factual and include relevant dates or amounts.</p>
        
        <textarea
          {...register('raw_description')}
          rows="5"
          className={`w-full bg-slate-900 border ${errors.raw_description ? 'border-red-500' : 'border-slate-700'} rounded-lg px-4 py-3 text-slate-100 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors resize-y`}
          placeholder="I purchased this item on Tuesday and immediately noticed that..."
        />
        {errors.raw_description && <p className="mt-1 text-sm text-red-400">{errors.raw_description.message}</p>}
      </div>

      {/* 3. Desired Resolution */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
        <h3 className="text-lg font-medium text-slate-100 mb-4">3. Desired Resolution</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Primary Outcome *</label>
            <select
              {...register('desired_resolution')}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-slate-100 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
            >
              {RESOLUTIONS.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Additional Details (Optional)</label>
            <input
              {...register('desired_resolution_details')}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-slate-100 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
              placeholder="e.g. Refund to original payment method"
            />
          </div>
        </div>
      </div>

      {/* 4. Your Details */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
        <h3 className="text-lg font-medium text-slate-100 mb-4">4. Your Details</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Full Name *</label>
            <input
              {...register('contact_name')}
              className={`w-full bg-slate-900 border ${errors.contact_name ? 'border-red-500' : 'border-slate-700'} rounded-lg px-4 py-2.5 text-slate-100 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors`}
            />
            {errors.contact_name && <p className="mt-1 text-sm text-red-400">{errors.contact_name.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Email Address *</label>
            <input
              type="email"
              {...register('contact_email')}
              className={`w-full bg-slate-900 border ${errors.contact_email ? 'border-red-500' : 'border-slate-700'} rounded-lg px-4 py-2.5 text-slate-100 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors`}
            />
            {errors.contact_email && <p className="mt-1 text-sm text-red-400">{errors.contact_email.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Phone Number (Optional)</label>
            <input
              {...register('contact_phone')}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-slate-100 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
            />
          </div>
        </div>
      </div>

      {/* Submit */}
      <div className="flex justify-end pt-4">
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-8 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-medium transition-colors shadow-md shadow-blue-600/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {isSubmitting ? (
            <>
              <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Drafting Letter...</span>
            </>
          ) : (
            <>
              <span className="material-icons text-[20px]">auto_awesome</span>
              <span>Generate Complaint</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
}
